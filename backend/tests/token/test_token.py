import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_token_refresh(api_client, get_tokens):
    url = reverse('user:token-refresh')
    response = api_client.post(url, data={'refresh': get_tokens['refresh']})
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_token_refresh_failure(api_client):
    url = reverse('user:token-refresh')
    response = api_client.post(url, data={'refresh': 'invalid-token'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_token_refresh_empty_body(api_client):
    url = reverse('user:token-refresh')
    response = api_client.post(url, data={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_token_verify(api_client, get_tokens):
    url = reverse('user:token-verify')
    response = api_client.post(url, data={'token': get_tokens['access']})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_token_verify_failure(api_client):
    url = reverse('user:token-verify')
    response = api_client.post(url, data={'token': 'invalid-token'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
