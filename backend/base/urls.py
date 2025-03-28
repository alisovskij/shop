from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/shop/', include('shop.urls')),
    path('api/v1/', include('user.urls')),
]
