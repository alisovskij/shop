from django.urls import path, include

from .views import FilterProducts, BasketListView, BasketOperationsView

urlpatterns = [
    path('products/', FilterProducts.as_view()),
    path('basket/', BasketListView.as_view()),  # GET/POST для списка
    path('basket/operations/', BasketOperationsView.as_view()),  # POST для добавления
    path('basket/operations/<int:pk>/', BasketOperationsView.as_view()),  # DELETE для удаления
]
