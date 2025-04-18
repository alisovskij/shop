from rest_framework import serializers

from .models import Product, Basket, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'image': {'required': False},
        }

class PaginationSerializer(serializers.Serializer):
    size = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False)


class BasketSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    product_description = serializers.CharField(source='product.description')

    class Meta:
        model = Basket
        fields = ('id', 'product_name', 'quantity', 'product_price', 'product_description')


class AddToBasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = ('product',  'quantity')
        extra_kwargs = {
            'quantity': {'required': False},
        }