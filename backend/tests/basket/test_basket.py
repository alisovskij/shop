import pytest
from django.urls import reverse
from rest_framework import status

from shop.models import Basket


@pytest.mark.django_db
def test_basket_list(api_client, get_tokens):
    url = reverse('shop:basket-list')

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_basket_list_no_token(api_client, get_tokens):
    url = reverse('shop:basket-list')

    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_basket_add_product(api_client, get_tokens, create_product):
    url = reverse('shop:basket-add')

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    data = {
        'product': create_product.id,
        'quantity': 1,
    }
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_201_CREATED

    basket = Basket.objects.get(product=response.data['basket_item']['id'])

    assert basket.product.name == create_product.name


@pytest.mark.django_db
def test_basket_add_no_authorization(api_client, get_tokens,):
    url = reverse('shop:basket-add')

    data = {
        'product': 'test',
        'quantity': 1,
    }
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize('product, quantity', [
    (1, 0),
    (0, 1),
    (0, 0),
    (-1, -1)
])
def test_basket_add_incorrect_product(api_client, get_tokens, product, quantity):
    url = reverse('shop:basket-add')

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    data = {
        'product': product,
        'quantity': quantity,
    }
    response = api_client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_basket_remove_product_success(api_client, get_tokens, create_basket_item):
    url = reverse('shop:basket-remove', kwargs={'pk': create_basket_item.id})

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_basket_remove_product_fail(api_client, get_tokens):
    url = reverse('shop:basket-remove', kwargs={'pk': 1})

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_basket_remove_product_no_authorization(api_client):
    url = reverse('shop:basket-remove', kwargs={'pk': 1})

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED



