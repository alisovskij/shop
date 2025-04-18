from django.urls import path

from user_profile.views import ChangePasswordView, GetAuthUserView

urlpatterns = [
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('me/', GetAuthUserView.as_view(), name='me'),
]
