from django.conf import settings
from rest_framework import permissions


class IsServiceOrWarehouseStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        service_token = request.headers.get("X-Service-Token")
        if service_token and service_token == settings.WAREHOUSE_API_TOKEN:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.groups.filter(
                    name__in=["WarehouseStaff", "WarehouseAdmins"]
                ).exists()
            )
        )


class IsWarehouseAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.groups.filter(name="WarehouseAdmins").exists()
            )
        )