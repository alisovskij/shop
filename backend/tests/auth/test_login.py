import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_auth_login_success(create_user, api_client):
    url = reverse('user:login')
    data = {'email': 'test@example.com', 'password': 'testpass123'}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data


@pytest.mark.django_db
def test_auth_login_invalid_password(create_user, api_client):
    url = reverse('user:login')
    data = {'email': 'test@example.com', 'password': 'invalidpass'}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_auth_login_invalid_email(create_user, api_client):
    url = reverse('user:login')
    data = {'email': 'invalid_email@example.com', 'password': 'testpass123'}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize('email,password', [
    ('', 'password123'),
    ('test@example.com', ''),
    ('', ''),
])
def test_auth_login_empty_fields(email, password, api_client):
    url = reverse('user:login')
    data = {'email': email, 'password': password}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_auth_login_not_email_verified(create_not_email_verified_user, api_client):
    url = reverse('user:login')
    data = {'email': 'test@example.com', 'password': 'testpass123'}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

