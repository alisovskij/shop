from rest_framework import serializers

class FilterParamsSerializer(serializers.Serializer):
    min_price = serializers.IntegerField(required=False)
    max_price = serializers.IntegerField(required=False)
    category = serializers.IntegerField(required=False)

class ProductSearchSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    filters = FilterParamsSerializer(required=False)
    page = serializers.IntegerField(required=False, default=1)
    page_size = serializers.IntegerField(required=False, default=10)