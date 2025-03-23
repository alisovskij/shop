from django.shortcuts import render
from rest_framework import viewsets, generics
from .models import CustomUser
from .serializers import UserSerializer, RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'head', 'options', 'delete']


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer