import pytest
from django.urls import reverse
from catalog.models import Category, CustomUser, Order, OrderItem
from catalog.forms import CustomUserCreationForm

# Generated with AI, reviewed and modified
@pytest.mark.django_db
class TestModelsAndForms:
    def test_category_str(self):
        category = Category.objects.create(name="Фантастика", slug="fiction")
        assert str(category) == "Фантастика"

    def test_book_str(self, book):
        assert str(book) == book.title

    def test_user_str(self, user):
        assert str(user) == user.username

    def test_orderitem_get_cost(self, order_item):
        assert order_item.get_cost() == order_item.price * order_item.quantity

    def test_order_get_total_cost(self, order, book):
        item1 = OrderItem.objects.create(order=order, book=book, price=100, quantity=1)
        item2 = OrderItem.objects.create(order=order, book=book, price=50, quantity=2)
        assert order.get_total_cost() == 200

    def test_order_default_paid_status(self, order):
        assert order.paid is False
        assert order.stripe_id == ""

    def test_book_default_stock(self, book):
        assert book.stock == 0

    def test_orderitem_default_quantity(self, order, book):
        item = OrderItem.objects.create(order=order, book=book, price=10)
        assert item.quantity == 1

    def test_register_form_valid(self):
        form = CustomUserCreationForm(data={'username': 'testuser', 'email': 't@t.com'})
        assert 'phone_number' in form.fields
        assert 'email' in form.fields

    def test_register_form_invalid_empty(self):
        form = CustomUserCreationForm(data={})
        assert not form.is_valid()


@pytest.mark.django_db
class TestViewsStatusCodes:
    def test_homepage_status(self, client):
        assert client.get(reverse('catalog:book_list')).status_code == 200

    def test_book_detail_status(self, client, book):
        assert client.get(reverse('catalog:book_detail', args=[book.pk])).status_code == 200

    def test_custom_user_password_check(self, user):
        assert user.check_password('password123') is True

    def test_custom_user_phone_number(self, user):
        user.phone_number = "+380991234567"
        user.save()
        assert user.phone_number == "+380991234567"

    def test_book_delete_page_status(self, client, book):
        assert client.get(reverse('catalog:book_delete', args=[book.pk])).status_code == 200

    def test_book_update_page_status(self, client, book):
        assert client.get(reverse('catalog:book_update', args=[book.pk])).status_code == 200

    def test_order_create_get(self, client):
        assert client.get(reverse('catalog:order_create')).status_code == 200

    def test_payment_success_get(self, client):
        assert client.get(reverse('catalog:payment_success')).status_code == 200

    def test_payment_cancel_get(self, client):
        assert client.get(reverse('catalog:payment_cancel')).status_code == 200

    def test_process_payment_no_session(self, client):
        assert client.get(reverse('catalog:process_payment')).status_code == 404

    def test_custom_user_is_active(self, user):
        assert user.is_active is True