import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_shop_categories_list(api_client, create_product):
    url = reverse('shop:category-list')
    response = api_client.get(url, {'page': 1, 'page_size': 10})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert  response.data['total_items'] == 1
