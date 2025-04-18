from django.core.cache import cache
from celery import shared_task
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from base import settings


@shared_task
def send_verification_email(user_id, domain):
    from django.contrib.auth import get_user_model
    user = get_user_model().objects.get(id=user_id)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = reverse('user:verify-email', kwargs={'uidb64': uid, 'token': token})
    full_url = f"http://{domain}{verify_url}"

    subject = "Подтверждение email"
    message = f"Привет, {user.username}!\n\nПодтвердите email по ссылке:\n{full_url}"

    send_mail(subject, message, None, [user.email])
    cache.set(f"email_token_{user.id}", token, timeout=3600)


@shared_task
def send_reset_password_email(email, reset_url):
    subject = 'Сброс пароля'
    message = f'Для сброса пароля перейдите по ссылке: {reset_url}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email])


