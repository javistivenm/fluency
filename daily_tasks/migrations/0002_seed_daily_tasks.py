from django.db import migrations


INITIAL_DAILY_TASKS = [
    ('Speaking alone', 1),
    ('Shadowing', 2),
    ('Phrase memorization', 3),
    ('Assisted writing', 4),
    ('Copywork', 5),
    ('Handwriting', 6),
    ('Anki', 7),
    ('Blinkist', 8),
    ('Busuu', 9),
    ('Cake', 10),
    ('TV Shows', 11),
    ('Word Trails', 12),
]


def seed_daily_tasks(apps, schema_editor):
    DailyTask = apps.get_model('daily_tasks', 'DailyTask')

    for task_name, sort_order in INITIAL_DAILY_TASKS:
        DailyTask.objects.update_or_create(
            name=task_name,
            defaults={
                'description': '',
                'is_active': True,
                'sort_order': sort_order,
            },
        )


def remove_seed_daily_tasks(apps, schema_editor):
    DailyTask = apps.get_model('daily_tasks', 'DailyTask')
    DailyTask.objects.filter(name__in=[task_name for task_name, _ in INITIAL_DAILY_TASKS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('daily_tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_daily_tasks, remove_seed_daily_tasks),
    ]
