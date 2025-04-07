from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_staff',)
    search_fields = UserAdmin.search_fields + ('email',)
    list_per_page = UserAdmin.list_per_page
