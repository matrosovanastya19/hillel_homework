from django.urls import path
from .views import (
    ReleaseStockAPIView,
    ReserveStockAPIView,
    RestockAPIView,
    StockDetailAPIView,
)

urlpatterns = [
    path("stock/<int:book_id>/", StockDetailAPIView.as_view(), name="stock_detail"),
    path("reserve/", ReserveStockAPIView.as_view(), name="stock_reserve"),
    path("release/", ReleaseStockAPIView.as_view(), name="stock_release"),
    path("restock/", RestockAPIView.as_view(), name="stock_restock"),
]