import logging
from celery import shared_task
from .models import StockItem

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock_alert(book_id: int, threshold: int = 5):
    try:
        item = StockItem.objects.get(book_id=book_id)
    except StockItem.DoesNotExist:
        return
    if item.available_quantity < threshold:
        logger.warning(
            "LOW STOCK ALERT: book_id=%s (SKU=%s) has only %s available!",
            item.book_id,
            item.sku,
            item.available_quantity,
        )