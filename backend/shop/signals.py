from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection

from .models import Product, Category, Basket


def clear_product_caches():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys('*products_*')
    for key in keys:
        redis_conn.delete(key)

def clear_category_caches():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys('*categories_*')
    for key in keys:
        redis_conn.delete(key)

def clear_basket_caches():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys('*basket_*')
    for key in keys:
        redis_conn.delete(key)

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    clear_product_caches()


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    clear_category_caches()


@receiver(post_save, sender=Basket)
@receiver(post_delete, sender=Basket)
def invalidate_basket_cache(sender, instance, **kwargs):
    clear_basket_caches()
