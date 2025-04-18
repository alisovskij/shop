import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_profile_me_success(api_client, get_tokens):
    url = reverse('profile:me')
    response = api_client.get(url, headers={'Content-type': 'application/json',
                                            'Authorization': f'Bearer {get_tokens['access']}'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == get_tokens['user']['username']
    assert response.data['email'] == get_tokens['user']['email']


@pytest.mark.django_db
def test_profile_me_wrong_token(api_client, get_tokens):
    url = reverse('profile:me')
    response = api_client.get(url, headers={'Content-type': 'application/json',
                                            'Authorization': f'Bearer {get_tokens['access']}f'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
