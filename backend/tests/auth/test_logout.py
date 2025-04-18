import pytest
from rest_framework import status
from django.urls import reverse


@pytest.mark.django_db
def test_auth_logout_success(api_client, get_tokens):
    url = reverse('user:logout')
    response = api_client.post(url, data={
        'refresh': get_tokens['refresh'],
    }, format='json', headers={"Content-Type": "application/json", 'Authorization': f'Bearer {get_tokens['access']}'})
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_auth_logout_invalid_token(api_client, get_tokens):
    url = reverse('user:logout')
    response = api_client.post(url, data={
        'refresh': get_tokens['refresh'],
    }, format='json', headers={"Content-Type": "application/json", 'Authorization': f'Bearer {get_tokens['access']}l'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_auth_logout_no_token(api_client, get_tokens):
    url = reverse('user:logout')
    response = api_client.post(url, data={
        'refresh': '',
    }, format='json', headers={"Content-Type": "application/json", 'Authorization': f'Bearer {get_tokens['access']}'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST

