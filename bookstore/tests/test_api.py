import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from catalog.models import Book, Category, Order, OrderItem
from tests.conftest import BookFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db, user):
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user

# Generated with AI, reviewed and modified
@pytest.mark.django_db
class TestBookAndCategoryAPI:
    # 1. Отримання списку категорій
    def test_get_categories_list(self, api_client, book):
        response = api_client.get(reverse('api-category-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    # 2. Заборона створення категорії для аноніма
    def test_create_category_anonymous_forbidden(self, api_client):
        response = api_client.post(reverse('api-category-list'), {'name': 'Sci-Fi', 'slug': 'sci-fi'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 3. Заборона створення категорії для звичайного юзера (не адміна)
    def test_create_category_regular_user_forbidden(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.post(reverse('api-category-list'), {'name': 'Sci-Fi', 'slug': 'sci-fi'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # 4. Успішне створення категорії адміном
    def test_create_category_admin_success(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(reverse('api-category-list'), {'name': 'Sci-Fi', 'slug': 'sci-fi'})
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(slug='sci-fi').exists()

    # 5. Отримання списку книг та перевірка Nested Serializer (category_detail)
    def test_get_books_with_nested_category(self, api_client, book):
        response = api_client.get(reverse('api-book-list'))
        assert response.status_code == status.HTTP_200_OK
        first_book = response.data['results'][0]
        assert 'category_detail' in first_book
        assert first_book['category_detail']['name'] == book.category.name

    # 6. Детальний перегляд однієї книги
    def test_get_single_book_detail(self, api_client, book):
        response = api_client.get(reverse('api-book-detail', args=[book.id]))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == book.title

    # 7. Створення книги адміном
    def test_create_book_admin(self, api_client, admin_user, book):
        api_client.force_authenticate(user=admin_user)
        data = {
            'title': 'DRF Guide',
            'author': 'Tom Christie',
            'description': 'REST API tutorial',
            'price': '45.00',
            'stock': 5,
            'category': book.category.id
        }
        response = api_client.post(reverse('api-book-list'), data)
        assert response.status_code == status.HTTP_201_CREATED

    # 8. Оновлення книги адміном (PATCH)
    def test_update_book_admin(self, api_client, admin_user, book):
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(reverse('api-book-detail', args=[book.id]), {'price': '99.99'})
        assert response.status_code == status.HTTP_200_OK
        book.refresh_from_db()
        assert str(book.price) == '99.99'

    # 9. Видалення книги адміном (DELETE)
    def test_delete_book_admin(self, api_client, admin_user, book):
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete(reverse('api-book-detail', args=[book.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(id=book.id).exists()

    # 10. Перевірка пагінації (20 елементів на сторінку)
    def test_book_pagination_20_items(self, api_client):
        BookFactory.create_batch(25)
        response = api_client.get(reverse('api-book-list'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20
        assert response.data['next'] is not None

    # 11. Фільтрація книг за категорією (django-filter)
    def test_book_filter_by_category(self, api_client, book):
        other_book = BookFactory()
        response = api_client.get(reverse('api-book-list'), {'category': book.category.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == book.id

    # 12. Пошук книг за назвою (SearchFilter)
    def test_book_search_filter(self, api_client, book):
        book.title = "UniqueHorcruxTitle"
        book.save()
        BookFactory()
        response = api_client.get(reverse('api-book-list'), {'search': 'UniqueHorcrux'})
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == "UniqueHorcruxTitle"


@pytest.mark.django_db
class TestJWTAndPermissions:
    # 13. Отримання JWT токена (Token Obtain)
    def test_jwt_obtain_token(self, api_client, user):
        response = api_client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'password123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    # 14. Оновлення JWT токена (Token Refresh)
    def test_jwt_refresh_token(self, api_client, user):
        obtain_resp = api_client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'password123'
        })
        refresh_token = obtain_resp.data['refresh']
        response = api_client.post(reverse('token_refresh'), {'refresh': refresh_token})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    # 15. Перевірка JWT токена (Token Verify)
    def test_jwt_verify_token(self, api_client, user):
        obtain_resp = api_client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'password123'
        })
        access_token = obtain_resp.data['access']
        response = api_client.post(reverse('token_verify'), {'token': access_token})
        assert response.status_code == status.HTTP_200_OK

    # 16. Помилка отримання JWT з неправильним паролем
    def test_jwt_invalid_credentials(self, api_client, user):
        response = api_client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'wrongpassword'
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 17. Доступ до захищеного ендпоінту з Bearer JWT токеном
    def test_access_orders_with_jwt_header(self, api_client, user):
        obtain_resp = api_client.post(reverse('token_obtain_pair'), {
            'username': user.username,
            'password': 'password123'
        })
        token = obtain_resp.data['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = api_client.get(reverse('api-order-list'))
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestOrdersAndCartAPI:
    # 18. Заборона перегляду замовлень для неавторизованих (IsAuthenticated)
    def test_orders_unauthenticated_denied(self, api_client):
        response = api_client.get(reverse('api-order-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 19. Створення замовлення авторизованим юзером
    def test_create_order_authenticated(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.post(reverse('api-order-list'), {
            'first_name': 'Anastasiia',
            'email': user.email
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1

    # 20. Перевірка Nested Serializer в Order (відображення items та total_cost)
    def test_order_nested_items_serialization(self, api_client, user, order_item):
        api_client.force_authenticate(user=user)
        order = order_item.order
        response = api_client.get(reverse('api-order-detail', args=[order.id]))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['items']) == 1
        assert response.data['total_cost'] == order.get_total_cost()

    # 21. Кастомний дозвіл IsOwnerOrReadOnly: власник може редагувати своє замовлення
    def test_owner_can_update_own_order(self, api_client, user, order):
        order.email = user.email
        order.save()
        api_client.force_authenticate(user=user)
        response = api_client.patch(reverse('api-order-detail', args=[order.id]), {'first_name': 'UpdatedName'})
        assert response.status_code == status.HTTP_200_OK

    # 22. Кастомний дозвіл IsOwnerOrReadOnly: інший юзер НЕ може редагувати чуже замовлення
    def test_other_user_cannot_update_order(self, api_client, user, order):
        order.email = "someone_else@example.com"
        order.save()
        api_client.force_authenticate(user=user)
        response = api_client.patch(reverse('api-order-detail', args=[order.id]), {'first_name': 'Hacker'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # 23. Перегляд порожнього кошика через API
    def test_cart_api_get_empty(self, api_client):
        response = api_client.get(reverse('api-cart-list'))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0

    # 24. Додавання книги в кошик через API
    def test_cart_api_add_book(self, api_client, book):
        response = api_client.post(reverse('api-cart-add'), {'book_id': book.id, 'quantity': 2})
        assert response.status_code == status.HTTP_200_OK
        assert str(book.id) in response.data['cart']

    # 25. Очищення кошика через API
    def test_cart_api_clear(self, api_client, book):
        api_client.post(reverse('api-cart-add'), {'book_id': book.id, 'quantity': 1})
        response = api_client.post(reverse('api-cart-clear'))
        assert response.status_code == status.HTTP_200_OK
        cart_resp = api_client.get(reverse('api-cart-list'))
        assert cart_resp.data['total_items'] == 0

    # 26. Перевірка доступності Swagger документації (/api/docs/)
    def test_swagger_docs_endpoint(self, api_client):
        response = api_client.get(reverse('swagger-ui'))
        assert response.status_code == status.HTTP_200_OK