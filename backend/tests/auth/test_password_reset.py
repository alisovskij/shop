import pytest
from django.urls import reverse
from django.core.cache import cache
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status


@pytest.mark.django_db
class TestResetPasswordView:

    def test_reset_password_success(self, api_client, create_user, mocker):
        mocker.patch('user.tasks.send_reset_password_email.delay')
        url = reverse('user:reset-password')
        response = api_client.post(url, {'email': create_user.email}, format='json')
        assert response.status_code == 200
        assert f'Письмо отправлено на {create_user.email}' in response.data['message']

    def test_reset_password_no_email(self, api_client):
        url = reverse('user:reset-password')
        response = api_client.post(url, {}, format='json')
        assert response.status_code == 400
        assert 'Email обязателен' in response.data['error']

    def test_reset_password_user_not_found(self, api_client):
        url = reverse('user:reset-password')
        response = api_client.post(url, {'email': 'unknown@example.com'}, format='json')
        assert response.status_code == 400
        assert 'Пользователь с таким email не найден' in response.data['message']


@pytest.mark.django_db
class TestResetPasswordConfirmView:

    def test_reset_password_confirm_success(self, api_client, create_user):
        uidb64 = urlsafe_base64_encode(force_bytes(create_user.pk))
        token = default_token_generator.make_token(create_user)

        cache.set(f"reset_password_{create_user.id}", token, timeout=3600)

        url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = api_client.post(url, {'password': 'newsecurepassword'}, format='json')

        assert response.status_code == 200
        assert 'Пароль успешно изменён' in response.data['message']

        create_user.refresh_from_db()
        assert create_user.check_password('newsecurepassword')

    def test_reset_password_confirm_invalid_uid(self, api_client):
        url = reverse('user:reset-password-confirm', kwargs={'uidb64': 'invalid', 'token': 'token'})
        response = api_client.post(url, {'password': 'newpassword123'}, format='json')
        assert response.status_code == 400
        assert 'Недействительная ссылка' in response.data['error']

    def test_reset_password_confirm_invalid_token(self, api_client, create_user):
        uidb64 = urlsafe_base64_encode(force_bytes(create_user.pk))
        url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': 'badtoken'})
        response = api_client.post(url, {'password': 'newpassword123'}, format='json')
        assert response.status_code == 400
        assert 'Невалидный или истёкший токен' in response.data['error']

    def test_reset_password_confirm_token_missing_in_cache(self, api_client, create_user):
        uidb64 = urlsafe_base64_encode(force_bytes(create_user.pk))
        token = default_token_generator.make_token(create_user)

        url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = api_client.post(url, {'password': 'newpassword123'}, format='json')
        assert response.status_code == 400
        assert 'Невалидный или истёкший токен' in response.data['error']

    def test_reset_password_confirm_missing_password(self, api_client, create_user):
        uidb64 = urlsafe_base64_encode(force_bytes(create_user.pk))
        token = default_token_generator.make_token(create_user)
        cache.set(f"reset_password_{create_user.id}", token, timeout=3600)
        url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        response = api_client.post(url, {}, format='json')
        assert response.status_code == 400
