from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class WarehouseUser(AbstractUser):
    department = models.CharField(_("Department"), max_length=100, blank=True)

    def __str__(self):
        return self.username


class StockItem(models.Model):
    book_id = models.PositiveIntegerField(_("Book ID"), unique=True, db_index=True)
    sku = models.CharField(_("SKU"), max_length=64, unique=True)
    quantity = models.PositiveIntegerField(_("Total quantity"), default=0)
    reserved_quantity = models.PositiveIntegerField(_("Reserved quantity"), default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_quantity(self) -> int:
        return max(self.quantity - self.reserved_quantity, 0)

    def __str__(self):
        return f"Book #{self.book_id} ({self.sku}) - avail: {self.available_quantity}"


class StockReservation(models.Model):
    order_id = models.PositiveIntegerField(_("Order ID"), db_index=True)
    stock_item = models.ForeignKey(
        StockItem, on_delete=models.CASCADE, related_name="reservations"
    )
    quantity = models.PositiveIntegerField(_("Quantity"))
    is_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order_id} -> Book #{self.stock_item.book_id} (x{self.quantity})"