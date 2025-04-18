from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('user.urls', 'user'), namespace='user')),
    path('api/shop/', include(('shop.urls', 'shop'), namespace='shop')),
    path('api/profile/', include(('user_profile.urls', 'profile'), namespace='profile')),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
