import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.parametrize("search, filters, page, page_size", [
    ("laptop", {"min_price": 1000, "max_price": 3000, "category": 1}, 1, 10),
    ("shirt", {"min_price": 10, "max_price": 100, "category": 2}, 1, 20),
    ("book", {"min_price": 0, "max_price": 50, "category": 5}, 1, 5),
    ("", {"min_price": 0, "max_price": 0}, 1, 10),
    ("gaming", {"min_price": 200, "max_price": 1500, "category": 87}, 1, 15),
    ("headphones", {"min_price": 50, "max_price": 500, "category": 2}, 1, 12),
    ("shoes", {"min_price": 30, "max_price": 300, "category": 6}, 1, 10),
    ("t-shirt", {"min_price": 5, "max_price": 50, "category": 4}, 1, 25),
    ("chair", {"min_price": 100, "max_price": 1000, "category": 3}, 1, 10),
    ("", {"min_price": 0, "max_price": 10000}, 1, 100),
])
def test_shop_products_filters(api_client, search, filters, page, page_size):
    url = reverse('shop:product-filters')
    data = {
        "search": search,
        "filters": filters,
        "page": page,
        "page_size": page_size,
    }
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_200_OK
