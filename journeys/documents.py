from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Journey


@registry.register_document
class JourneyDocument(Document):
    class Index:
        # Name of the Elasticsearch index
        name = 'journeys'
        departure_station_name = fields.KeywordField(fielddata=True)
        return_station_name = fields.KeywordField(fielddata=True)

        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Journey # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'id',
            'departure_time',
            'return_time',
            'departure_station_name',
            'return_station_name',
            'covered_distance',
            'duration',
        ]