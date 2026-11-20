from rest_framework import serializers
from .models import StockItem


class StockItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = StockItem
        fields = [
            "book_id",
            "sku",
            "quantity",
            "reserved_quantity",
            "available_quantity",
            "updated_at",
        ]


class ReserveItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class ReserveRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    items = ReserveItemSerializer(many=True, allow_empty=False)


class ReleaseRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)


class RestockSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(min_value=1)
    sku = serializers.CharField(max_length=64, required=False)
    quantity = serializers.IntegerField(min_value=1)