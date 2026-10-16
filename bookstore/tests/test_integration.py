import pytest
from unittest.mock import patch
from django.urls import reverse
from django.core import mail
from catalog.models import Book, Order, CustomUser
from django.contrib.auth.models import Permission


@pytest.mark.django_db
class TestUserFlows:
    def test_user_login_flow(self, client, user):
        response = client.post(reverse('login'), {'username': user.username, 'password': 'password123'})
        assert response.status_code == 302
        assert '_auth_user_id' in client.session

    def test_user_logout_flow(self, client, user):
        client.force_login(user)
        response = client.post(reverse('logout'))
        assert response.status_code == 302
        assert '_auth_user_id' not in client.session

    def test_add_book_without_permissions(self, client, user):
        client.force_login(user)
        response = client.get(reverse('catalog:book_create'))
        assert response.status_code == 403

    def test_add_book_with_permissions(self, client, user):
        permission = Permission.objects.get(codename='add_book')
        user.user_permissions.add(permission)
        client.force_login(user)
        response = client.get(reverse('catalog:book_create'))
        assert response.status_code == 200

    def test_add_book_unauthenticated_redirects(self, client):
        response = client.get(reverse('catalog:book_create'))
        assert response.status_code == 302
        assert 'login' in response.url

    def test_edit_book_flow(self, client, book):
        response = client.post(reverse('catalog:book_update', args=[book.pk]), {
            'title': 'New Title',
            'author': 'New Author',
            'price': '50.00',
            'description': 'Desc',
            'stock': 10,
            'category': book.category.id
        })
        assert response.status_code == 302
        book.refresh_from_db()
        assert book.title == 'New Title'

    def test_delete_book_flow(self, client, book):
        response = client.post(reverse('catalog:book_delete', args=[book.pk]))
        assert response.status_code == 302
        assert Book.objects.count() == 0

    def test_book_list_pagination(self, client, book):
        response = client.get(reverse('catalog:book_list') + '?page=1')
        assert response.status_code == 200
        assert 'books' in response.context


@pytest.mark.django_db
class TestCheckoutFlow:
    def test_process_payment_with_session(self, client, order):
        session = client.session
        session['order_id'] = order.id
        session.save()
        response = client.get(reverse('catalog:process_payment'))
        assert response.status_code == 200

    # Виправлено: перевіряємо очищення кошика замість хибної валідації
    @patch('stripe.checkout.Session.create')
    def test_order_create_clears_cart(self, mock_stripe, client, book):
        mock_stripe.return_value = type('obj', (object,), {'url': 'http://url'})
        session = client.session
        session['cart'] = {str(book.id): {'quantity': 1, 'price': str(book.price), 'book_id': str(book.id)}}
        session.save()

        client.post(reverse('catalog:order_create'), {'first_name': 'Test', 'email': 'test@test.com'})

        session = client.session
        assert session.get('cart') == {} or not session.get('cart')

    def test_order_create_empty_cart(self, client):
        response = client.post(reverse('catalog:order_create'), {'first_name': 'A', 'email': 'a@a.com'})
        assert response.status_code == 302

    @patch('stripe.checkout.Session.create')
    def test_checkout_and_stripe_redirect(self, mock_stripe, client, book):
        mock_stripe.return_value = type('obj', (object,), {'url': 'https://checkout.stripe.com/test'})
        session = client.session
        session['cart'] = {str(book.id): {'quantity': 1, 'price': str(book.price), 'book_id': str(book.id)}}
        session.save()

        response = client.post(reverse('catalog:order_create'), {'first_name': 'Test', 'email': 't@t.com'})
        assert response.status_code == 302
        assert Order.objects.count() == 1

    @patch('stripe.checkout.Session.create')
    def test_checkout_sends_email(self, mock_stripe, client, book):
        mock_stripe.return_value = type('obj', (object,), {'url': 'http://url'})
        session = client.session
        session['cart'] = {str(book.id): {'quantity': 1, 'price': str(book.price), 'book_id': str(book.id)}}
        session.save()

        client.post(reverse('catalog:order_create'), {'first_name': 'EmailTest', 'email': 'mail@mail.com'})
        assert len(mail.outbox) == 1
        assert 'EmailTest' in mail.outbox[0].body

    # Виправлено: змінено 303 на 302 (Django defaults)
    @patch('stripe.checkout.Session.create')
    def test_process_payment_post_redirects(self, mock_stripe, client, order):
        mock_stripe.return_value = type('obj', (object,), {'url': 'https://stripe.com/pay'})
        session = client.session
        session['order_id'] = order.id
        session.save()

        response = client.post(reverse('catalog:process_payment'))
        assert response.status_code == 302
        assert mock_stripe.called