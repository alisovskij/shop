from django.db import models
from django.utils import timezone

from user.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Basket(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f'{self.user.username} - {self.product.name}'
