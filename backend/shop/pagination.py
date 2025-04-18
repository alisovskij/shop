from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


    def get_page_size(self, request):
        if request.method == 'POST' and 'page_size' in request.data:
            try:
                page_size = int(request.data['page_size'])
                if page_size > self.max_page_size:
                    return self.max_page_size
                if page_size <= 0:
                    return self.page_size
                return page_size
            except (TypeError, ValueError):
                pass
        return super().get_page_size(request)

    def get_page_number(self, request, paginator):
        if request.method == 'POST' and 'page' in request.data:
            try:
                return int(request.data['page'])
            except (TypeError, ValueError):
                pass
        return super().get_page_number(request, paginator)
    
    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'size': self.page.paginator.per_page,
            'total_pages': self.page.paginator.num_pages,
            'total_items': self.page.paginator.count,
            'results': data
        })