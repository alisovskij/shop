import pytest
from rest_framework import status
from django.urls import reverse


@pytest.mark.django_db
def test_auth_register_success(user_data, api_client):
    url = reverse('user:register')
    response = api_client.post(url, data=user_data, format='json')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_auth_register_user_is_exists(user_data, create_user, api_client):
    url = reverse('user:register')
    response = api_client.post(url, data=user_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize('email,password', [
    ('example@example.com', '1234567'),
    ('example1@example.com', '123456789'),
    ('example2@example.com', '123456789qwe'),
    ('example3examplecom', '1234567qwerty'),
    ('', '')
])
def test_auth_register_common_password_and_invalid_email(email, password, db, api_client):
    url = reverse('user:register')
    data = {
        'username': 'test',
        'password': password,
        'email': email,
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

