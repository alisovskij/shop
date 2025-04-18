import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_profile_change_password_success(api_client, get_tokens, user_data):
    url = reverse('profile:change-password')
    new_password = 'newsecurepassword'

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    response = api_client.post(url, data={
        'old_password': user_data['password'],
        'new_password': new_password,
    }, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data.get('detail') == 'Пароль успешно изменён'

    user = get_user_model().objects.get(email=user_data['email'])

    assert user.check_password(new_password)


@pytest.mark.django_db
def test_profile_change_password_incorrect_old_password(api_client, get_tokens, user_data):
    url = reverse('profile:change-password')
    new_password = 'newsecurepassword'

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    response = api_client.post(url, data={
        'old_password': 'incorrectpassword',
        'new_password': new_password,
    }, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_profile_change_password_no_authorization(api_client, get_tokens, user_data):
    url = reverse('profile:change-password')
    new_password = 'newsecurepassword'

    response = api_client.post(url, data={
        'old_password': user_data['password'],
        'new_password': new_password,
    }, format='json')

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize('password', [
    '1234567',
    '123456789',
    '1Qwerty',
    '123456789qwe'
])
def test_profile_change_password_common_password(api_client, get_tokens, user_data, password):
    url = reverse('profile:change-password')

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {get_tokens["access"]}')

    response = api_client.post(url, data={
        'old_password': user_data['password'],
        'new_password': password,
    }, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

