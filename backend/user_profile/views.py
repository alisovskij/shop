from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import  UserSerializer
from .serializers import ChangePasswordSerializer


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer, status_code=status.HTTP_200_OK,
        tags=['profile'],
        operation_description="Смена пароля в профиле"
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Пароль успешно изменён'}, status=status.HTTP_200_OK)


class GetAuthUserView(APIView):
    @swagger_auto_schema(
        operation_description="Получение пользователя сессии",
        tags=['profile']
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        data = {
            "username": serializer.data.get('username'),
            "email": serializer.data.get('email'),
            "first_name": serializer.data.get('first_name'),
            "last_name": serializer.data.get('last_name')
        }
        return Response(data, status=status.HTTP_200_OK)