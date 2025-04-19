import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema

from .tasks import send_reset_password_email
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    MyTokenObtainPairSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    http_method_names = ['get', 'head', 'options', 'delete']

    @swagger_auto_schema(
        operation_description="Получить список всех пользователей",
        responses={status.HTTP_200_OK: UserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        logger.info("Получение списка пользователей")
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получить пользователя по ID",
        responses={status.HTTP_200_OK: UserSerializer()}
    )
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Получение пользователя по ID: {kwargs.get('pk')}")
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Удалить пользователя по ID",
        responses={status.HTTP_204_NO_CONTENT: "Удалено успешно"}
    )
    def destroy(self, request, *args, **kwargs):
        logger.warning(f"Удаление пользователя с ID: {kwargs.get('pk')}")
        return super().destroy(request, *args, **kwargs)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Регистрация нового пользователя",
        responses={201: openapi.Response('Успешная регистрация', RegisterSerializer)},
        tags=['authenticate']
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 201:
            logger.info(f"Успешная регистрация пользователя: {request.data.get('email')}")
        return response


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Авторизация пользователя. Возвращает access и refresh токены",
        responses={200: openapi.Response('Успешная авторизация', LoginResponseSerializer)},
        tags=['authenticate']
    )
    def post(self, request, *args, **kwargs):
        logger.info(f"Попытка входа: {request.data.get('email')}")
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f"Успешный вход: {request.data.get('email')}")
        else:
            logger.warning(f"Неудачная попытка входа: {request.data.get('email')}")
        return response


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=LogoutSerializer,
        operation_description="Выход пользователя(refresh_token становится невалидным)",
        tags=['authenticate']
    )
    def post(self, request):
        logger.info(f"Пользователь {request.user} выходит из системы")
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"Пользователь {request.user} успешно вышел")
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=ResetPasswordRequestSerializer,
        tags=['authenticate'],
        operation_description="Восстановление пароля в случае, если пользователь его забыл"
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            logger.warning("Запрос восстановления пароля без email")
            return Response({'error': 'Email обязателен'}, status=400)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Пользователь не найден при попытке восстановления пароля: {email}")
            return Response({'message': 'Пользователь с таким email не найден'}, status=400)

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        cache_key = f"reset_password_{user.id}"
        cache.set(cache_key, token, timeout=3600)

        domain = get_current_site(request).domain
        verify_url = reverse('user:reset-password-confirm', kwargs={'uidb64': uidb64, 'token': token})
        full_url = f"http://{domain}{verify_url}"

        send_reset_password_email.delay(user.email, full_url)
        logger.info(f"Письмо для восстановления пароля отправлено на: {user.email}")

        return Response({'message': f'Письмо отправлено на {user.email}'}, status=200)


class ResetPasswordConfirmView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        request_body=ResetPasswordConfirmSerializer,
        tags=['authenticate'],
        operation_description="Окончательная смена пароля"
    )
    def post(self, request, uidb64, token):
        logger.info("Запрос на подтверждение смены пароля")
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(f"Ошибка при декодировании или поиске пользователя: {e}")
            return Response({'error': 'Недействительная ссылка'}, status=400)

        if not default_token_generator.check_token(user, token) or cache.get(f"reset_password_{user.id}") != token:
            logger.warning(f"Невалидный или истёкший токен для пользователя {user.email}")
            return Response({'error': 'Невалидный или истёкший токен'}, status=400)

        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get('password')
        if not password:
            logger.warning("Пустой пароль при подтверждении сброса")
            return Response({'error': 'Пароль обязателен'}, status=400)

        user.set_password(password)
        user.save()
        cache.delete(f"reset_password_{user.id}")
        logger.info(f"Пароль успешно изменён для пользователя: {user.email}")
        return Response({'message': 'Пароль успешно изменён'}, status=200)
