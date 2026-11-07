from rest_framework import serializers
from .models import Category, Book, Order, OrderItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BookSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'description', 'price', 'stock', 'category', 'category_detail']

class OrderItemSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source='book', read_only=True)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)
    cost = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'book_detail', 'price', 'quantity', 'cost']

    def get_cost(self, obj):
        return obj.get_cost()

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'email', 'created', 'paid', 'stripe_id', 'items', 'total_cost']
        read_only_fields = ['created', 'paid', 'stripe_id']

    def get_total_cost(self, obj):
        return obj.get_total_cost()

class CartAddSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)