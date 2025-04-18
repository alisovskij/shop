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


class ResendEmailVerificationView(APIView):
    @swagger_auto_schema(
        operation_description="Отправка повторного письма с подтверждением почты",
        tags=['authenticate']
    )
    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        cache_key = f"verify_email:{user.id}"
        if cache.get(cache_key):
            return Response(
                {"detail": "Письмо уже отправлено. Попробуйте снова через минуту."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if user.is_email_verified:
            return Response({"message": "Email уже подтвержден"}, status=status.HTTP_200_OK)

        domain = get_current_site(request).domain
        send_verification_email.delay(user.id, domain)
        cache.set(cache_key, True, timeout=60)

        return Response({"message": "Письмо с подтверждение email выслано"}, status=status.HTTP_200_OK)


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
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Неверная ссылка'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token) and cache.get(f"email_token_{user.id}") == token:
            user.is_email_verified = True
            user.save()
            cache.delete(f"email_token_{user.id}")
            return Response({'message': 'Email успешно подтверждён'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Недействительный или просроченный токен'}, status=status.HTTP_400_BAD_REQUEST)
