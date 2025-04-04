from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
)
from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .documents import ProductDocument
from .serializers import ProductDocumentSerializer


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
        if self.request.method == 'POST' and self.request.data:
            search_query = self.request.data.get('search')
            filters = self.request.data.get('filters', {})

            queryset = super().get_queryset()

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
                    if field.startswith('category.'):
                        nested_path = field.split('.')[0]
                        nested_field = field.split('.')[1]
                        queryset = queryset.filter(
                            'nested',
                            path=nested_path,
                            query=Q('term', **{f'{nested_path}.{nested_field}': value})
                        )
                    elif isinstance(value, dict):
                        queryset = queryset.filter('range', **{field: value})
                    else:
                        queryset = queryset.filter('term', **{field: value})

            return queryset

        return super().get_queryset()

    def create(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)