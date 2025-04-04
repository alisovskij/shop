from django.urls import path
from .views import ProductDocumentView

urlpatterns = [
    path('', ProductDocumentView.as_view({'get': 'list', 'post': 'create'}), name='product-search'),
]