from django.test import TestCase

# Create your tests here.
from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import override_settings
from rest_framework.test import APIClient

from inventory.models import StockItem, StockReservation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_headers():
    return {"HTTP_X_SERVICE_TOKEN": settings.WAREHOUSE_API_TOKEN}


@pytest.fixture
def stock_item(db):
    return StockItem.objects.create(
        book_id=10,
        sku="BOOK-10",
        quantity=5,
        reserved_quantity=0,
    )


@pytest.mark.django_db
@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
def test_unauthorized_request_is_rejected(api_client, stock_item):
    response = api_client.get(f"/api/warehouse/stock/{stock_item.book_id}/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
def test_get_stock_with_service_token(api_client, auth_headers, stock_item):
    response = api_client.get(
        f"/api/warehouse/stock/{stock_item.book_id}/", **auth_headers
    )
    assert response.status_code == 200
    assert response.data["book_id"] == 10
    assert response.data["available_quantity"] == 5


@pytest.mark.django_db
@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
@patch("inventory.views.check_low_stock_alert.delay")
def test_reserve_stock_success(mock_alert, api_client, auth_headers, stock_item):
    payload = {
        "order_id": 101,
        "items": [{"book_id": stock_item.book_id, "quantity": 3}],
    }
    response = api_client.post(
        "/api/warehouse/reserve/", payload, format="json", **auth_headers
    )
    assert response.status_code == 200
    assert response.data == {"status": "reserved", "order_id": 101}

    stock_item.refresh_from_db()
    assert stock_item.reserved_quantity == 3
    assert stock_item.available_quantity == 2
    assert StockReservation.objects.filter(
        order_id=101, stock_item=stock_item, quantity=3, is_released=False
    ).exists()
    mock_alert.assert_called_once_with(stock_item.book_id)


@pytest.mark.django_db
@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
def test_reserve_stock_insufficient_returns_409(api_client, auth_headers, stock_item):
    payload = {
        "order_id": 102,
        "items": [{"book_id": stock_item.book_id, "quantity": 99}],
    }
    response = api_client.post(
        "/api/warehouse/reserve/", payload, format="json", **auth_headers
    )
    assert response.status_code == 409

    stock_item.refresh_from_db()
    assert stock_item.reserved_quantity == 0


@pytest.mark.django_db
@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
@patch("inventory.views.check_low_stock_alert.delay")
def test_release_stock_restores_availability(
    mock_alert, api_client, auth_headers, stock_item
):
    api_client.post(
        "/api/warehouse/reserve/",
        {"order_id": 103, "items": [{"book_id": stock_item.book_id, "quantity": 2}]},
        format="json",
        **auth_headers,
    )

    response = api_client.post(
        "/api/warehouse/release/",
        {"order_id": 103},
        format="json",
        **auth_headers,
    )
    assert response.status_code == 200
    assert response.data == {"status": "released", "order_id": 103}

    stock_item.refresh_from_db()
    assert stock_item.reserved_quantity == 0
    assert stock_item.available_quantity == 5
    assert StockReservation.objects.get(order_id=103).is_released is True