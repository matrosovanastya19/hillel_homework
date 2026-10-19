import pytest
import factory
from catalog.models import Book, Category, CustomUser, Order, OrderItem

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
    name = factory.Faker('word')
    slug = factory.Faker('slug')

class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book
    title = factory.Faker('sentence', nb_words=3)
    author = factory.Faker('name')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    description = factory.Faker('text')
    category = factory.SubFactory(CategoryFactory)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    # Хешуємо пароль для логіну
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order
    first_name = factory.Faker('first_name')
    email = factory.Faker('email')

class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem
    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    price = 150.00
    quantity = 2

@pytest.fixture
def book(db):
    return BookFactory()

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.fixture
def order(db):
    return OrderFactory()

@pytest.fixture
def order_item(db):
    return OrderItemFactory()