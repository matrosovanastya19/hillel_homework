import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class WarehouseError(Exception):
    """Базова помилка при збої зв'язку зі складом."""


class InsufficientStockError(WarehouseError):
    """На складі недостатньо книг для резервування."""


class WarehouseClient:
    """HTTP-клієнт для REST API комунікації з ProjectB (Warehouse)."""

    def __init__(self):
        self.base_url = settings.WAREHOUSE_SERVICE_URL.rstrip("/")
        self.headers = {
            "X-Service-Token": settings.WAREHOUSE_API_TOKEN,
            "Content-Type": "application/json",
        }
        self.timeout = (3, 5)  # 3 сек на з'єднання, 5 сек на відповідь

    def get_stock(self, book_id: int) -> int | None:
        url = f"{self.base_url}/api/warehouse/stock/{book_id}/"
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 404:
                logger.warning("Stock record not found for book_id=%s", book_id)
                return 0
            response.raise_for_status()
            data = response.json()
            logger.info("Fetched stock for book_id=%s: %s", book_id, data)
            return data.get("available_quantity", 0)
        except requests.RequestException as exc:
            logger.error("Failed to fetch stock for book_id=%s: %s", book_id, exc)
            return None

    def reserve_books(self, order_id: int, items: list[dict]) -> dict:
        """
        items: [{"book_id": 1, "quantity": 2}, ...]
        """
        url = f"{self.base_url}/api/warehouse/reserve/"
        payload = {"order_id": order_id, "items": items}
        try:
            logger.info("Reserving stock in Warehouse for order_id=%s", order_id)
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=self.timeout
            )
            if response.status_code == 409:
                detail = response.json().get("detail", "Not enough items in stock")
                logger.warning(
                    "Insufficient stock for order_id=%s: %s", order_id, detail
                )
                raise InsufficientStockError(detail)

            response.raise_for_status()
            logger.info("Stock reserved successfully for order_id=%s", order_id)
            return response.json()

        except requests.Timeout as exc:
            logger.error("Warehouse timeout for order_id=%s", order_id, exc_info=True)
            raise WarehouseError("Warehouse service timed out") from exc
        except requests.RequestException as exc:
            logger.error("Warehouse request failed for order_id=%s: %s", order_id, exc)
            raise WarehouseError("Warehouse service is unavailable") from exc

    def release_books(self, order_id: int) -> bool:
        url = f"{self.base_url}/api/warehouse/release/"
        try:
            logger.info("Releasing stock reservation for order_id=%s", order_id)
            response = requests.post(
                url,
                json={"order_id": order_id},
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return True
        except requests.RequestException as exc:
            logger.error("Failed to release stock for order_id=%s: %s", order_id, exc)
            raise WarehouseError("Failed to release stock") from exc
