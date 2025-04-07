from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/shop/', include('shop.urls')),
    path('api/', include('user.urls')),
    path('api/search/', include('search.urls')),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),  # Swagger UI
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)