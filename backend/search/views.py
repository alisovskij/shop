from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
)
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .documents import ProductDocument
from .serializers import ProductDocumentSerializer


class ProductSearchService:
    @staticmethod
    def search_products(validated_data):
        search_query = validated_data.get('search')
        filters = validated_data.get('filters', {})

        queryset = ProductDocument.search()

        if search_query:
            queryset = queryset.query(
                'multi_match',
                query=search_query,
                fields=['name^3', 'description^1', 'category.name^2'],
                fuzziness='AUTO',
                prefix_length=1,
                max_expansions=50
            )

        if filters:
            for field, value in filters.items():
                if field == "min_price":
                    queryset = queryset.filter('range', price={'gte': value})
                elif field == "max_price":
                    queryset = queryset.filter('range', price={'lte': value})
                elif field == "category":
                    queryset = queryset.filter('term', category__id=value)
                else:
                    queryset = queryset.filter('term', **{field: value})

        return queryset


class ProductDocumentView(DocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    filter_backends = [
        CompoundSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
    ]
    search_fields = {
        'name': {
            'field': 'name',
            'analyzer': 'standard',
            'fuzziness': 'AUTO',
            'boost': 2
        },
        'description': {
            'field': 'description',
            'fuzziness': 2,
            'prefix_length': 1
        },
        'category.name': {
            'field': 'category.name',
            'analyzer': 'russian_morphology_analyzer'
        }
    }
    filter_fields = {
        'quantity': 'quantity',
        'price': 'price',
        'name.raw': 'name',
        'category.id': 'category.id',
    }
    ordering_fields = {
        'price': 'price',
        'quantity': 'quantity',
    }
    suggest_fields = {
        'name_suggest': {
            'field': 'name.suggest',
            'suggesters': ['completion'],
        },
    }
    ordering = ('-price',)
    parser_classes = [JSONParser]

    def get_queryset(self):
        if not self.request.data:
            return super().get_queryset()

        return ProductSearchService.search_products(self.request.data)

    def create(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
