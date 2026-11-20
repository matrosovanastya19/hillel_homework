from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Order, OrderItem, Book, Category, CustomUser


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


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "phone_number", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("phone_number",)}),
    )
