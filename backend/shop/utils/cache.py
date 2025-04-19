import hashlib
import json
import logging
from django.core.cache import cache
from rest_framework.response import Response

logger = logging.getLogger(__name__)

def get_cached_list_response(request, timeout: int = 600, prefix: str = "", extra_params: dict = None,
                             get_response_data=None):
    page = int(request.query_params.get('page', 1)) if int(request.query_params.get('page', 1)) > 0 else 1
    page_size = int(request.query_params.get('page_size', 10)) if int(request.query_params.get('page_size', 10)) > 0 else 10

    base_data = {
        "page": page,
        "page_size": page_size,
    }

    if extra_params:
        base_data.update(extra_params)

    key_base = prefix + json.dumps(base_data, sort_keys=True)
    cache_key = f"{prefix}{hashlib.md5(key_base.encode()).hexdigest()}"

    logger.info(f"Сформирован ключ кеша: {cache_key}")

    cached_data = cache.get(cache_key)
    if cached_data:
        logger.info(f"Найдено кешированное значение для ключа {cache_key}. Возвращаем данные из кеша.")
        return Response(cached_data)

    if get_response_data:
        logger.info(f"Кеш для ключа {cache_key} не найден. Получение данных с использованием функции get_response_data.")
        response = get_response_data()
        cache.set(cache_key, response.data, timeout)
        logger.info(f"Данные успешно сохранены в кеш с ключом {cache_key}.")
        return response
    else:
        logger.warning(f"Метод получения данных не передан для кеширования с ключом {cache_key}.")
        return Response({"error": "Метод получения данных не передан."}, status=400)
