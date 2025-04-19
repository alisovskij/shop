import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_redis import get_redis_connection

from .models import Product, Category, Basket

logger = logging.getLogger(__name__)

def clear_product_caches():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys('*products_*')
    for key in keys:
        redis_conn.delete(key)
        logger.info(f"Кеш с ключом {key} для продуктов был удалён.")

def clear_category_caches():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys('*categories_*')
    for key in keys:
        redis_conn.delete(key)
        logger.info(f"Кеш с ключом {key} для категорий был удалён.")

def clear_basket_caches():
    redis_conn = get_redis_connection("default")
    keys = redis_conn.keys('*basket_*')
    for key in keys:
        redis_conn.delete(key)
        logger.info(f"Кеш с ключом {key} для корзины был удалён.")

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    logger.info(f"Изменения или удаление продукта с ID {instance.id}. Очистка кеша продуктов.")
    clear_product_caches()


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    logger.info(f"Изменения или удаление категории с ID {instance.id}. Очистка кеша категорий.")
    clear_category_caches()


@receiver(post_save, sender=Basket)
@receiver(post_delete, sender=Basket)
def invalidate_basket_cache(sender, instance, **kwargs):
    logger.info(f"Изменения или удаление товара из корзины для пользователя с ID {instance.user.id}. Очистка кеша корзины.")
    clear_basket_caches()
