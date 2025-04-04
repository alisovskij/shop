from django.core.management.base import BaseCommand
from shop.models import Product, Category
from faker import Faker
import random

RUSSIAN_PRODUCT_NAMES = [
    "Смартфон", "Ноутбук", "Телевизор", "Наушники", "Планшет",
    "Кофемашина", "Микроволновая печь", "Холодильник", "Пылесос",
    "Фен", "Утюг", "Чайник", "Блендер", "Монитор", "Клавиатура",
    "Мышь", "Роутер", "Фитнес-браслет", "Умные часы", "Колонка"
]

RUSSIAN_ADJECTIVES = [
    "новый", "мощный", "стильный", "компактный", "профессиональный",
    "умный", "бюджетный", "премиальный", "энергоэффективный", "удобный",
    "прочный", "легкий", "беспроводной", "водонепроницаемый", "эргономичный"
]

# Предопределенные категории
CATEGORIES = [
    {"name": "Электроника"},
    {"name": "Бытовая техника"},
    {"name": "Компьютеры"},
    {"name": "Аксессуары"},
    {"name": "Гаджеты"},
]


class Command(BaseCommand):
    help = 'Заполняет базу данных товарами на русском языке с категориями'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Количество товаров для создания')

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')
        total = kwargs['total']

        # Создаем категории, если их нет
        self.create_categories()

        # Получаем все существующие категории
        categories = list(Category.objects.all())

        for _ in range(total):
            # Генерируем название товара
            product_name = random.choice(RUSSIAN_PRODUCT_NAMES)
            adjective = random.choice(RUSSIAN_ADJECTIVES)
            name = f"{adjective.capitalize()} {product_name}"

            # Создаем товар с случайной категорией
            Product.objects.create(
                name=name,
                description=self.generate_russian_description(fake, product_name),
                price=round(random.uniform(500, 50000), 2),
                quantity=random.randint(1, 100),
                category=random.choice(categories)  # Добавляем случайную категорию
            )

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {total} товаров с категориями'))

    def create_categories(self):
        """Создает категории, если они не существуют"""
        for category_data in CATEGORIES:
            Category.objects.get_or_create(
                name=category_data["name"],            )
        self.stdout.write(self.style.SUCCESS('Категории созданы/проверены'))

    def generate_russian_description(self, fake, product_name):
        descriptions = [
            f"Этот {product_name.lower()} обладает превосходными характеристиками и надежностью.",
            f"Инновационный {product_name.lower()} для вашего комфорта и удобства.",
            f"Высококачественный {product_name.lower()} с современным дизайном.",
            f"Популярная модель {product_name.lower()} с улучшенными параметрами.",
            f"Профессиональный {product_name.lower()} для требовательных пользователей."
        ]
        return random.choice(descriptions) + " " + fake.paragraph(nb_sentences=2)