from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Book

@receiver(post_save, sender=Book)
@receiver(post_delete, sender=Book)
def invalidate_book_cache(sender, instance, **kwargs):
    """Очищає кеш при зміні або видаленні книги."""
    cache.delete(f'book_detail_{instance.id}')
    cache.clear()