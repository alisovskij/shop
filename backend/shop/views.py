from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from search.serializers import ProductDocumentSerializer
from search.views import ProductSearchService
from .filters import ProductSearchSerializer
from .models import Product, Basket, Category
from .pagination import CustomPagination
from .serializers import ProductSerializer, BasketSerializer, AddToBasketSerializer, CategorySerializer
from .utils.cache import get_cached_list_response


class CategoryListView(ListAPIView):
    queryset = Category.objects.all().order_by('-id')
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        operation_description="Получение всех категорий",
        tags=['products'],
    )
    def get(self, request, *args, **kwargs):
        return get_cached_list_response(
            request,
            prefix="categories_",
            get_response_data=lambda: super(CategoryListView, self).list(request, *args, **kwargs)
        )


class ProductListView(ListAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_description="Получение всех продуктов",
        tags=['products'],
    )
    def get(self, request, *args, **kwargs):
        return get_cached_list_response(
            request,
            prefix="products_",
            get_response_data=lambda: super(ProductListView, self).list(request, *args, **kwargs)
        )


class ProductSearchView(APIView):
    pagination_class = CustomPagination

    @swagger_auto_schema(
        request_body=ProductSearchSerializer,
        responses={200: ProductSerializer(many=True)},
        operation_description="Поиск продуктов по фильтрам(Каждое поле не обязательно)",
        tags=['products']
    )
    def post(self, request, *args, **kwargs):
        self.serializer = ProductSearchSerializer(data=request.data)
        self.serializer.is_valid(raise_exception=True)

        search = self.serializer.validated_data.get("search", None)
        filters = self.serializer.validated_data.get("filters", {})
        page = self.serializer.validated_data.get("page", 1)
        page_size = self.serializer.validated_data.get("page_size", 10)

        extra_params = {
            "search": search,
            "filters": filters,
            "page": page,
            "page_size": page_size
        }
        return get_cached_list_response(
            request,
            get_response_data=self.get_response_data,
            timeout=60 * 15,
            prefix="products_search_",
            extra_params=extra_params
        )

    def get_response_data(self):
        filter_kwargs = {}
        search = self.serializer.validated_data.get("search", None)
        filters = self.serializer.validated_data.get("filters", {})

        if search is not None:
            request_data = self.serializer.initial_data
            queryset = ProductSearchService.search_products(request_data)
        else:
            if 'min_price' in filters:
                filter_kwargs['price__gte'] = filters['min_price']
            if 'max_price' in filters:
                filter_kwargs['price__lte'] = filters['max_price']
            if 'category_id' in filters:
                filter_kwargs['category_id'] = filters['category_id']
            queryset = Product.objects.filter(**filter_kwargs).order_by('-id')

        paginator = self.pagination_class()
        paginated = paginator.paginate_queryset(queryset, self.request, view=self)
        serializer = ProductDocumentSerializer(paginated, many=True) if search is not None else ProductSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)


class BasketListView(ListAPIView):
    serializer_class = BasketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Basket.objects.filter(user=self.request.user).order_by('-id')

    @swagger_auto_schema(
        operation_description="Просмотр корзины зарегистрированного пользователя",
        tags=['basket']
    )
    def get(self, request, *args, **kwargs):
        return get_cached_list_response(
            request,
            prefix="basket_",
            get_response_data=lambda: super(BasketListView, self).list(request, *args, **kwargs)
        )


class BasketCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToBasketSerializer

    @swagger_auto_schema(
        request_body=AddToBasketSerializer,
        operation_description="Добавление ранее не созданного товара или обновление его количества в корзине",
        tags=['basket']
    )

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
            if quantity > 1:
                basket_item.quantity = quantity
            else:
                basket_item.quantity += 1
            basket_item.save()

        basket_serializer = BasketSerializer(basket_item)

        return Response({
            "message": "Товар успешно добавлен в корзину.",
            "basket_item": basket_serializer.data,
        }, status=status.HTTP_201_CREATED)


class BasketDeleteView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddToBasketSerializer

    @swagger_auto_schema(
        operation_description="Удаление товара из корзины по id",
        tags=['basket']
    )
    def delete(self, request, pk):
        user = request.user
        basket_item = get_object_or_404(Basket, id=pk, user=user)
        basket_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
