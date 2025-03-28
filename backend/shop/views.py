from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from .models import Product, Basket
from .pagination import CustomPagination
from .serializers import ProductSerializer, BasketSerializer, AddToBasketSerializer


class FilterProducts(APIView):
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        queryset = Product.objects.all().order_by('-id')
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class BasketListView(APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def post(self, request):
        queryset = Basket.objects.filter(user=request.user).order_by('-id')
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        serializer = BasketSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class BasketOperationsView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        serializer = AddToBasketSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)

        basket_item, created = Basket.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            basket_item.quantity += quantity if quantity else 1
            basket_item.save()

        return Response({"message": "Товар успешно добавлен в корзину."}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        user = request.user
        basket_item = get_object_or_404(Basket, id=pk, user=user)
        basket_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)