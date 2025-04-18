from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import RegisterView, LoginView, LogoutView, UserViewSet, ResetPasswordView, ResetPasswordConfirmView
from .email_services import VerifyEmailView, ResendEmailVerificationView

router = DefaultRouter()
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/reset-password/<str:uidb64>/<str:token>/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verify-email/<int:user_id>/', ResendEmailVerificationView.as_view(), name='resend-verify-email'),
]