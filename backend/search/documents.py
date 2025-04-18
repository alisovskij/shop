from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from shop.models import Product, Category


@registry.register_document
class ProductDocument(Document):
    name = fields.TextField(
        analyzer='russian_morphology_analyzer',
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
            'fuzzy': fields.TextField(analyzer='russian_morphology_analyzer')
        }
    )

    description = fields.TextField(analyzer='russian_morphology_analyzer')

    category = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(
            analyzer='russian_morphology_analyzer',
            fields={
                'raw': fields.KeywordField()
            }
        ),
    })

    product_image = fields.KeywordField()

    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'filter': {
                    'russian_stemmer': {
                        'type': 'stemmer',
                        'language': 'russian'
                    },
                    'russian_stop': {
                        'type': 'stop',
                        'stopwords': '_russian_'
                    }
                },
                'analyzer': {
                    'russian_morphology_analyzer': {
                        'type': 'custom',
                        'tokenizer': 'standard',
                        'filter': ['lowercase', 'russian_stemmer', 'russian_stop']
                    }
                }
            }
        }

    class Django:
        model = Product
        fields = ['id', 'price', 'quantity', 'image']
        related_models = [Category]

    def get_queryset(self):
        return super().get_queryset().select_related('category')

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Category):
            return related_instance.products.all()