from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StockItem, StockReservation, WarehouseUser


@admin.register(WarehouseUser)
class WarehouseUserAdmin(UserAdmin):
    list_display = ("username", "email", "department", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Warehouse Info", {"fields": ("department",)}),
    )


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ("book_id", "sku", "quantity", "reserved_quantity", "available_quantity", "updated_at")
    search_fields = ("book_id", "sku")


@admin.register(StockReservation)
class StockReservationAdmin(admin.ModelAdmin):
    list_display = ("order_id", "stock_item", "quantity", "is_released", "created_at")
    list_filter = ("is_released",)
