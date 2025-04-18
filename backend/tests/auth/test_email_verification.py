import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from django.core.cache import cache

@pytest.mark.django_db
def test_verify_email_success(api_client, create_not_email_verified_user):
    user = create_not_email_verified_user
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    cache.set(f"email_token_{user.id}", token, timeout=3600)

    url = reverse('user:verify-email', kwargs={'uidb64': uidb64, 'token': token})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == 'Email успешно подтверждён'

    user.refresh_from_db()
    assert user.is_email_verified is True
    assert cache.get(f"email_token_{user.id}") is None

@pytest.mark.django_db
def test_verify_email_invalid_token( api_client, create_not_email_verified_user):
    user = create_not_email_verified_user
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = 'invalid-token'

    cache.set(f"email_token_{user.id}", 'another-valid-token', timeout=3600)

    url = reverse('user:verify-email', kwargs={'uidb64': uidb64, 'token': invalid_token})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Недействительный или просроченный токен' in response.data['error']
    user.refresh_from_db()
    assert user.is_email_verified is False

@pytest.mark.django_db
def test_verify_email_expired_or_missing_token(api_client, create_not_email_verified_user):
    user = create_not_email_verified_user
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    url = reverse('user:verify-email', kwargs={'uidb64': uidb64, 'token': token})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Недействительный или просроченный токен' in response.data['error']
    user.refresh_from_db()
    assert user.is_email_verified is False