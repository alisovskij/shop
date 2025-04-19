import logging
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import UserSerializer
from .serializers import ChangePasswordSerializer

logger = logging.getLogger(__name__)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer, status_code=status.HTTP_200_OK,
        tags=['profile'],
        operation_description="Смена пароля в профиле"
    )
    def post(self, request):
        logger.info(f"Попытка смены пароля для пользователя с ID {request.user.id}")

        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if not serializer.is_valid():
            logger.warning(f"Ошибка валидации данных для пользователя с ID {request.user.id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        logger.info(f"Пароль успешно изменён для пользователя с ID {request.user.id}")
        return Response({'detail': 'Пароль успешно изменён'}, status=status.HTTP_200_OK)


class GetAuthUserView(APIView):
    @swagger_auto_schema(
        operation_description="Получение пользователя сессии",
        tags=['profile']
    )
    def get(self, request):
        logger.info(f"Запрос информации о пользователе сессии для пользователя с ID {request.user.id}")
        if not request.user.is_authenticated:
            logger.warning("Попытка получения неавторизованного пользователя")
            return Response({"detail":"Пользователь не авторизирован"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(request.user)
        data = {
            "username": serializer.data.get('username'),
            "email": serializer.data.get('email'),
            "first_name": serializer.data.get('first_name'),
            "last_name": serializer.data.get('last_name')
        }

        logger.info(f"Информация о пользователе с ID {request.user.id} успешно получена")
        return Response(data, status=status.HTTP_200_OK)
