from django.contrib import admin
from .models import Order, OrderItem, Book, Category


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["book"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "email", "paid", "created"]
    list_filter = ["paid", "created"]
    inlines = [OrderItemInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "price"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
