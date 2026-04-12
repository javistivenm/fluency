from django_summernote.apps import DjangoSummernoteConfig


class SummernoteAutoFieldConfig(DjangoSummernoteConfig):
    default_auto_field = 'django.db.models.AutoField'
