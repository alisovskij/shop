from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import Product, Category, Basket


class MyAdminSite(AdminSite):
    site_header = "Моя компания"
    site_title = "Администрирование"
    index_title = "Добро пожаловать в панель управления"

admin_site = MyAdminSite(name='myadmin')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'category', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    list_editable = ('price', 'quantity')
    list_per_page = 50


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    list_per_page = 50

@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user', 'product')
    list_per_page = 50