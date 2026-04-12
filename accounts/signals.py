from django.apps import apps as django_apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


ADMIN_GROUP_NAME = 'Admin'
USER_GROUP_NAME = 'Usuario'
ADMIN_PERMISSION_MAP = {
    'accounts': ['add_user', 'change_user', 'delete_user', 'view_user'],
    'support_library': [
        'add_mediatitle',
        'change_mediatitle',
        'delete_mediatitle',
        'view_mediatitle',
        'add_season',
        'change_season',
        'delete_season',
        'view_season',
        'add_episode',
        'change_episode',
        'delete_episode',
        'view_episode',
    ],
    'daily_tasks': [
        'add_dailytask',
        'change_dailytask',
        'delete_dailytask',
        'view_dailytask',
        'add_userdailytaskstatus',
        'change_userdailytaskstatus',
        'delete_userdailytaskstatus',
        'view_userdailytaskstatus',
    ],
}


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs):
    admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP_NAME)
    Group.objects.get_or_create(name=USER_GROUP_NAME)

    using = kwargs.get('using')
    verbosity = kwargs.get('verbosity', 0)
    migration_apps = kwargs.get('apps') or django_apps

    for app_label, permission_codenames in ADMIN_PERMISSION_MAP.items():
        app_config = django_apps.get_app_config(app_label)
        create_permissions(app_config, verbosity=verbosity, using=using, apps=migration_apps)
        admin_permissions = Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=permission_codenames,
        )
        admin_group.permissions.add(*admin_permissions)
