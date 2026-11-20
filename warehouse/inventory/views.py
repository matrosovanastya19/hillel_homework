from django.shortcuts import render

# Create your views here.
import logging
from django.core.cache import cache
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StockItem, StockReservation
from .permissions import IsServiceOrWarehouseStaff, IsWarehouseAdmin
from .serializers import (
    ReleaseRequestSerializer,
    ReserveRequestSerializer,
    RestockSerializer,
    StockItemSerializer,
)
from .tasks import check_low_stock_alert

logger = logging.getLogger(__name__)


class BaseWarehouseAPIView(APIView):
    """Базовий CBV для всіх ендпоінтів складу: спільні права та робота з кешем."""

    permission_classes = [IsServiceOrWarehouseStaff]

    @staticmethod
    def get_stock_cache_key(book_id: int) -> str:
        return f"warehouse_stock_{book_id}"

    def invalidate_stock_cache(self, book_id: int) -> None:
        cache.delete(self.get_stock_cache_key(book_id))


class StockDetailAPIView(BaseWarehouseAPIView):
    """GET /api/warehouse/stock/<book_id>/ — залишок конкретної книги з кешем."""

    def get(self, request, book_id: int):
        cache_key = self.get_stock_cache_key(book_id)
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        stock_item = get_object_or_404(StockItem, book_id=book_id)
        data = StockItemSerializer(stock_item).data
        cache.set(cache_key, data, timeout=300)
        return Response(data)


class ReserveStockAPIView(BaseWarehouseAPIView):
    """POST /api/warehouse/reserve/ — резервування книг під order_id з ProjectA."""

    def post(self, request):
        serializer = ReserveRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]
        items = serializer.validated_data["items"]

        with transaction.atomic():
            book_ids = [item["book_id"] for item in items]
            stock_map = {
                s.book_id: s
                for s in StockItem.objects.select_for_update().filter(
                    book_id__in=book_ids
                )
            }

            for item in items:
                stock = stock_map.get(item["book_id"])
                if not stock or stock.available_quantity < item["quantity"]:
                    logger.warning(
                        "Insufficient stock for order_id=%s, book_id=%s",
                        order_id,
                        item["book_id"],
                    )
                    return Response(
                        {
                            "detail": _("Not enough items in stock for book #%s")
                            % item["book_id"]
                        },
                        status=status.HTTP_409_CONFLICT,
                    )

            for item in items:
                stock = stock_map[item["book_id"]]
                stock.reserved_quantity += item["quantity"]
                stock.save(update_fields=["reserved_quantity", "updated_at"])
                StockReservation.objects.create(
                    order_id=order_id,
                    stock_item=stock,
                    quantity=item["quantity"],
                )
                self.invalidate_stock_cache(stock.book_id)
                check_low_stock_alert.delay(stock.book_id)

        logger.info("Reserved stock for order_id=%s (%s items)", order_id, len(items))
        return Response(
            {"status": "reserved", "order_id": order_id},
            status=status.HTTP_200_OK,
        )


class ReleaseStockAPIView(BaseWarehouseAPIView):
    """POST /api/warehouse/release/ — скасування резерву для order_id."""

    def post(self, request):
        serializer = ReleaseRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data["order_id"]

        with transaction.atomic():
            reservations = (
                StockReservation.objects.select_for_update()
                .select_related("stock_item")
                .filter(order_id=order_id, is_released=False)
            )
            for res in reservations:
                stock = res.stock_item
                stock.reserved_quantity = max(stock.reserved_quantity - res.quantity, 0)
                stock.save(update_fields=["reserved_quantity", "updated_at"])
                res.is_released = True
                res.save(update_fields=["is_released"])
                self.invalidate_stock_cache(stock.book_id)

        logger.info("Released stock reservation for order_id=%s", order_id)
        return Response({"status": "released", "order_id": order_id})


class RestockAPIView(BaseWarehouseAPIView):
    """POST /api/warehouse/restock/ — поповнення складу (тільки WarehouseAdmins)."""

    permission_classes = [IsWarehouseAdmin]

    def post(self, request):
        serializer = RestockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_id = serializer.validated_data["book_id"]
        qty = serializer.validated_data["quantity"]
        sku = serializer.validated_data.get("sku") or f"BOOK-{book_id}"

        stock, created = StockItem.objects.get_or_create(
            book_id=book_id,
            defaults={"sku": sku, "quantity": qty},
        )
        if not created:
            stock.quantity += qty
            stock.save(update_fields=["quantity", "updated_at"])

        self.invalidate_stock_cache(book_id)
        return Response(StockItemSerializer(stock).data, status=status.HTTP_200_OK)