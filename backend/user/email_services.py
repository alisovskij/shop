import logging
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import send_verification_email
from .serializers import User

logger = logging.getLogger(__name__)


class ResendEmailVerificationView(APIView):
    @swagger_auto_schema(
        operation_description="Отправка повторного письма с подтверждением почты",
        tags=['authenticate']
    )
    def post(self, request, user_id):
        logger.info(f"Попытка отправить повторное письмо с подтверждением для пользователя с ID {user_id}")

        user = get_object_or_404(User, id=user_id)

        cache_key = f"verify_email:{user.id}"
        if cache.get(cache_key):
            logger.warning(
                f"Слишком много запросов: письмо с подтверждением уже отправлено для пользователя с ID {user_id}")
            return Response(
                {"detail": "Письмо уже отправлено. Попробуйте снова через минуту."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if user.is_email_verified:
            logger.info(f"Почта уже подтверждена для пользователя с ID {user_id}")
            return Response({"message": "Email уже подтвержден"}, status=status.HTTP_200_OK)

        domain = get_current_site(request).domain
        logger.info(f"Отправка письма с подтверждением на почту пользователя с ID {user_id} на домен {domain}")
        send_verification_email.delay(user.id, domain)

        cache.set(cache_key, True, timeout=60)
        logger.info(f"Письмо с подтверждением отправлено для пользователя с ID {user_id}, кэш установлен")

        return Response({"message": "Письмо с подтверждением email выслано"}, status=status.HTTP_200_OK)


class VerifyEmailView(APIView):
    @swagger_auto_schema(
        operation_description="Подтверждение email",
        tags=['authenticate'],
        manual_parameters=[
            openapi.Parameter('uidb64', openapi.IN_PATH, description="UID пользователя", type=openapi.TYPE_STRING),
            openapi.Parameter('token', openapi.IN_PATH, description="Токен подтверждения", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, uidb64, token):
        logger.info(f"Попытка подтвердить email с uidb64 {uidb64}")

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            logger.info(f"Пользователь найден для uidb64 {uidb64}: user_id {user.id}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Ошибка при декодировании uidb64 или пользователь не найден: {e}")
            return Response({'error': 'Неверная ссылка'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token) and cache.get(f"email_token_{user.id}") == token:
            logger.info(f"Токен действителен для пользователя с ID {user.id}. Подтверждаем email.")
            user.is_email_verified = True
            user.save()
            cache.delete(f"email_token_{user.id}")
            logger.info(f"Email успешно подтверждён для пользователя с ID {user.id}")
            return Response({'message': 'Email успешно подтверждён'}, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Недействительный или просроченный токен для пользователя с ID {user.id}")
            return Response({'error': 'Недействительный или просроченный токен'}, status=status.HTTP_400_BAD_REQUEST)
