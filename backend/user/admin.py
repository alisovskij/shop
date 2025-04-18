from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля', {'fields': ('is_email_verified',)}),
    )
    list_display = ('id', ) + UserAdmin.list_display + ('is_email_verified',)
    search_fields = UserAdmin.search_fields + ('email',)
    list_per_page = UserAdmin.list_per_page
