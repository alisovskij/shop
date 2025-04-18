from django.urls import path, include

from .views import ProductSearchView, BasketListView, BasketCreateView, BasketDeleteView, ProductListView, CategoryListView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/filters/', ProductSearchView.as_view(), name='product-filters'),
    path('basket/', BasketListView.as_view(), name='basket-list'),
    path('basket/add/', BasketCreateView.as_view(), name='basket-add'),
    path('basket/remove/<int:pk>/', BasketDeleteView.as_view(), name='basket-remove'),
]
