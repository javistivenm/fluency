from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone


SEED_USERNAME = 'support_library_seed'
CASTLEVANIA_SLUG = 'castlevania-nocturne'
BLACK_MIRROR_SLUG = 'black-mirror'


def build_episode_html(series_name, season_number, episode_number):
    return f'''
<h2>Before You Watch</h2>
<p>This sample support page helps learners prepare for <strong>{series_name}</strong>, season {season_number}, episode {episode_number}.</p>
<h3>What To Notice</h3>
<ul>
  <li>Listen for repeated expressions that reveal tension, fear, or strategy.</li>
  <li>Watch how characters interrupt, react, and change tone in fast dialogue.</li>
  <li>Pay attention to descriptive verbs and adjectives that build the episode atmosphere.</li>
</ul>
<h3>Vocabulary Focus</h3>
<ul>
  <li><strong>clue</strong>: a detail that helps you understand what is happening</li>
  <li><strong>threat</strong>: something dangerous that may cause harm</li>
  <li><strong>warning</strong>: a message that tells you to be careful</li>
</ul>
<h3>Useful Questions</h3>
<blockquote>
  What new expression did you understand before watching? Which line sounded important for the main conflict?
</blockquote>
<p>Edit this sample content with your own notes, vocabulary, grammar points, and episode-specific guidance.</p>
'''


def create_seed_data(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    MediaTitle = apps.get_model('support_library', 'MediaTitle')
    Season = apps.get_model('support_library', 'Season')
    Episode = apps.get_model('support_library', 'Episode')

    seed_user, _ = User.objects.get_or_create(
        username=SEED_USERNAME,
        defaults={
            'email': 'support-library-seed@local.invalid',
            'password': make_password(None),
            'is_active': False,
            'is_staff': False,
            'is_superuser': False,
        },
    )

    now = timezone.now()

    castlevania, _ = MediaTitle.objects.update_or_create(
        slug=CASTLEVANIA_SLUG,
        defaults={
            'title': 'Castlevania: Nocturne',
            'kind': 'series',
            'summary': 'Sample support library entry for season 2, designed to help learners preview vocabulary, tone, and key dialogue before watching.',
            'is_active': True,
            'movie_content': '',
            'movie_content_status': 'draft',
            'published_at': None,
            'created_by_id': seed_user.id,
            'updated_by_id': seed_user.id,
        },
    )
    castlevania_season, _ = Season.objects.update_or_create(
        media_title_id=castlevania.id,
        number=2,
        defaults={
            'title': 'Season 2',
            'is_active': True,
        },
    )
    for episode_number in range(1, 9):
        Episode.objects.update_or_create(
            season_id=castlevania_season.id,
            number=episode_number,
            defaults={
                'title': f'Episode {episode_number}',
                'content': build_episode_html('Castlevania: Nocturne', 2, episode_number),
                'status': 'published',
                'is_active': True,
                'published_at': now,
                'created_by_id': seed_user.id,
                'updated_by_id': seed_user.id,
            },
        )

    black_mirror, _ = MediaTitle.objects.update_or_create(
        slug=BLACK_MIRROR_SLUG,
        defaults={
            'title': 'Black Mirror',
            'kind': 'series',
            'summary': 'Sample support library entry for season 3, ready to be expanded with episode-specific vocabulary, cultural notes, and comprehension support.',
            'is_active': True,
            'movie_content': '',
            'movie_content_status': 'draft',
            'published_at': None,
            'created_by_id': seed_user.id,
            'updated_by_id': seed_user.id,
        },
    )
    black_mirror_season, _ = Season.objects.update_or_create(
        media_title_id=black_mirror.id,
        number=3,
        defaults={
            'title': 'Season 3',
            'is_active': True,
        },
    )
    for episode_number in range(1, 7):
        Episode.objects.update_or_create(
            season_id=black_mirror_season.id,
            number=episode_number,
            defaults={
                'title': f'Episode {episode_number}',
                'content': build_episode_html('Black Mirror', 3, episode_number),
                'status': 'published',
                'is_active': True,
                'published_at': now,
                'created_by_id': seed_user.id,
                'updated_by_id': seed_user.id,
            },
        )


def remove_seed_data(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    MediaTitle = apps.get_model('support_library', 'MediaTitle')

    MediaTitle.objects.filter(slug__in=[CASTLEVANIA_SLUG, BLACK_MIRROR_SLUG]).delete()
    User.objects.filter(username=SEED_USERNAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('support_library', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_seed_data, remove_seed_data),
    ]
