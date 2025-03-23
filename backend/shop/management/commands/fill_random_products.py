import random
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import Product, Category

class Command(BaseCommand):
    help = 'Fill the database with random products'

    def handle(self, *args, **kwargs):
        fake = Faker()
        categories = Category.objects.all()

        if not categories.exists():
            self.stdout.write(self.style.ERROR('No categories found. Please create some categories first.'))
            return

        for _ in range(10):
            name = fake.word()
            description = fake.text(max_nb_chars=100)
            quantity = random.randint(1, 100)
            category = random.choice(categories)
            price = round(random.uniform(10, 1000), 2)

            product = Product(
                name=name,
                description=description,
                quantity=quantity,
                category=category,
                price=price
            )
            product.save()

        self.stdout.write(self.style.SUCCESS('Successfully filled the database with random products'))