from rest_framework import serializers

class ProductDocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
