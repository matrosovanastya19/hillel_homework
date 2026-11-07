from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Category, Book, Order
from .serializers import CategorySerializer, BookSerializer, OrderSerializer, CartAddSerializer
from .permissions import IsOwnerOrReadOnly
from .cart import Cart


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API для категорій.
    Читати можуть усі, створювати/редагувати/видаляти — тільки адміністратор (IsAdminUser).
    """
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


class BookViewSet(viewsets.ModelViewSet):
    """
    API для книг з підтримкою фільтрації, пошуку та пагінації.
    Редагування доступне тільки адміністраторам.
    """
    queryset = Book.objects.select_related('category').all().order_by('id')
    serializer_class = BookSerializer
    filterset_fields = ['category', 'author', 'stock']
    search_fields = ['title', 'description', 'author']
    ordering_fields = ['price', 'title']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]


class OrderViewSet(viewsets.ModelViewSet):
    """
    API для замовлень.
    Доступ тільки для авторизованих (IsAuthenticated) + перевірка власника (IsOwnerOrReadOnly).
    """
    queryset = Order.objects.prefetch_related('items__book__category').all().order_by('-created')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        if not serializer.validated_data.get('email') and self.request.user.email:
            serializer.save(email=self.request.user.email)
        else:
            serializer.save()


class CartViewSet(viewsets.ViewSet):
    """
    API для управління кошиком (на базі сесій).
    """
    permission_classes = [AllowAny]

    def list(self, request):
        """Отримати вміст кошика (GET /api/cart/)."""
        cart = Cart(request)
        return Response({
            'items': cart.cart,
            'total_items': len(cart.cart),
            'total_price': cart.get_total_price() if hasattr(cart, 'get_total_price') else 0
        })

    @action(detail=False, methods=['post'])
    def add(self, request):
        """Додати книгу в кошик (POST /api/cart/add/)."""
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = get_object_or_404(Book, id=serializer.validated_data['book_id'])
        cart = Cart(request)

        if hasattr(cart, 'add'):
            cart.add(book=book, quantity=serializer.validated_data['quantity'])
        else:
            book_id = str(book.id)
            if book_id not in cart.cart:
                cart.cart[book_id] = {'quantity': 0, 'price': str(book.price), 'book_id': book.id}
            cart.cart[book_id]['quantity'] += serializer.validated_data['quantity']
            request.session.modified = True

        return Response({'status': 'Book added to cart', 'cart': cart.cart}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Очистити кошик (POST /api/cart/clear/)."""
        cart = Cart(request)
        cart.clear()
        return Response({'status': 'Cart cleared'}, status=status.HTTP_200_OK)