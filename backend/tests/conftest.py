from unicodedata import category

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from shop.models import Product, Category, Basket

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'is_email_verified': True
    }


@pytest.fixture
def create_not_email_verified_user(user_data, db):
    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        is_email_verified=False,
        password=user_data['password']
    )
    return user


@pytest.fixture
def create_user(user_data, db):
    return User.objects.create_user(**user_data)


@pytest.fixture
def get_tokens(create_user):
    client = APIClient()
    url = reverse('user:login')
    response = client.post(url, data={
        'email': create_user.email,
        'password': 'testpass123'
    }, format='json')
    assert response.status_code == status.HTTP_200_OK
    return response.data


@pytest.fixture
def create_product():
    category = Category.objects.create(name='Test Category')
    product = Product.objects.create(name='Test Product', price=100, quantity=1, description='Test Description', category=category)
    return product


@pytest.fixture
def create_basket_item(create_user, create_product):
    basket = Basket.objects.create(user=create_user, product=create_product)
    return basket