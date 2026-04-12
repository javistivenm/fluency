from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.signals import ADMIN_GROUP_NAME, USER_GROUP_NAME

from .forms import EpisodeForm, MediaTitleForm
from .models import Episode, MediaTitle, Season

User = get_user_model()


class SupportLibraryModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='model-user', password='StrongPassword123!')

    def test_media_title_full_clean_rejects_published_movie_without_content(self):
        # Arrange
        media_title = MediaTitle(
            title='Movie Without Content',
            kind=MediaTitle.Kind.MOVIE,
            movie_content='',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=self.user,
            updated_by=self.user,
        )

        # Act / Assert
        with self.assertRaises(ValidationError):
            media_title.full_clean()

    def test_media_title_save_clears_movie_fields_for_series(self):
        # Arrange
        media_title = MediaTitle.objects.create(
            title='Series With Wrong Movie Content',
            kind=MediaTitle.Kind.SERIES,
            movie_content='<p>This should be removed.</p>',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=self.user,
            updated_by=self.user,
        )

        # Act
        media_title.refresh_from_db()

        # Assert
        self.assertEqual(media_title.movie_content, '')
        self.assertEqual(media_title.movie_content_status, MediaTitle.ContentStatus.DRAFT)
        self.assertIsNone(media_title.published_at)
        self.assertEqual(media_title.slug, 'series-with-wrong-movie-content')

    def test_season_full_clean_rejects_movie_title(self):
        # Arrange
        movie = MediaTitle.objects.create(
            title='Movie Base',
            kind=MediaTitle.Kind.MOVIE,
            movie_content='<p>Movie support.</p>',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=self.user,
            updated_by=self.user,
        )
        season = Season(media_title=movie, number=1)

        # Act / Assert
        with self.assertRaises(ValidationError):
            season.full_clean()

    def test_episode_save_sets_published_at_only_for_published_entries(self):
        # Arrange
        series = MediaTitle.objects.create(
            title='Episode Save Series',
            kind=MediaTitle.Kind.SERIES,
            created_by=self.user,
            updated_by=self.user,
        )
        season = Season.objects.create(media_title=series, number=1)
        episode = Episode.objects.create(
            season=season,
            number=1,
            title='Draft Episode',
            content='<p>Draft support.</p>',
            status=Episode.Status.DRAFT,
            created_by=self.user,
            updated_by=self.user,
        )

        # Act
        draft_published_at = episode.published_at
        episode.status = Episode.Status.PUBLISHED
        episode.save()
        episode.refresh_from_db()

        # Assert
        self.assertIsNone(draft_published_at)
        self.assertIsNotNone(episode.published_at)


class SupportLibraryFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='form-user', password='StrongPassword123!')
        cls.series = MediaTitle.objects.create(
            title='Form Series',
            kind=MediaTitle.Kind.SERIES,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.season = Season.objects.create(media_title=cls.series, number=1)

    def test_media_title_form_rejects_published_movie_without_content(self):
        # Arrange
        form = MediaTitleForm(
            data={
                'title': 'Invalid Movie',
                'kind': MediaTitle.Kind.MOVIE,
                'summary': 'Movie summary',
                'is_active': True,
                'movie_content_status': MediaTitle.ContentStatus.PUBLISHED,
                'movie_content': '',
            }
        )

        # Act
        is_valid = form.is_valid()

        # Assert
        self.assertFalse(is_valid)
        self.assertIn('movie_content', form.errors)

    def test_episode_form_accepts_rich_content_payload(self):
        # Arrange
        form = EpisodeForm(
            data={
                'number': 1,
                'title': 'Episode Form',
                'status': Episode.Status.PUBLISHED,
                'is_active': True,
                'content': '<p>Rich text content</p>',
            }
        )

        # Act
        is_valid = form.is_valid()

        # Assert
        self.assertTrue(is_valid)


class SupportLibraryPermissionTests(TestCase):
    def test_admin_group_receives_support_library_permissions(self):
        admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)

        self.assertTrue(admin_group.permissions.filter(codename='view_mediatitle').exists())
        self.assertTrue(admin_group.permissions.filter(codename='add_mediatitle').exists())
        self.assertTrue(admin_group.permissions.filter(codename='change_episode').exists())


class SupportLibrarySeedDataTests(TestCase):
    def test_seed_titles_exist_after_migrations(self):
        self.assertTrue(MediaTitle.objects.filter(title='Castlevania: Nocturne').exists())
        self.assertTrue(MediaTitle.objects.filter(title='Black Mirror').exists())

    def test_seed_seasons_and_episode_counts_exist(self):
        castlevania = MediaTitle.objects.get(title='Castlevania: Nocturne')
        black_mirror = MediaTitle.objects.get(title='Black Mirror')

        self.assertEqual(castlevania.seasons.get(number=2).episodes.count(), 8)
        self.assertEqual(black_mirror.seasons.get(number=3).episodes.count(), 6)


class SupportLibraryViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
        cls.user_group = Group.objects.get(name=USER_GROUP_NAME)
        cls.admin_user = User.objects.create_user(username='library-admin', password='StrongPassword123!')
        cls.admin_user.groups.add(cls.admin_group)
        cls.normal_user = User.objects.create_user(username='library-user', password='StrongPassword123!')
        cls.normal_user.groups.add(cls.user_group)

        cls.movie = MediaTitle.objects.create(
            title='Arrival',
            kind=MediaTitle.Kind.MOVIE,
            summary='A sci-fi movie support page.',
            movie_content='<p>Published movie support content.</p>',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )
        cls.series = MediaTitle.objects.create(
            title='Friends',
            kind=MediaTitle.Kind.SERIES,
            summary='Friends support library.',
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )
        cls.season = Season.objects.create(media_title=cls.series, number=1, title='Season 1')
        cls.published_episode = Episode.objects.create(
            season=cls.season,
            number=1,
            title='The Pilot',
            content='<p>Published episode support content with pilot-keyword.</p>',
            status=Episode.Status.PUBLISHED,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )
        cls.draft_episode = Episode.objects.create(
            season=cls.season,
            number=2,
            title='Draft Episode',
            content='<p>Draft episode support content.</p>',
            status=Episode.Status.DRAFT,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )
        cls.second_published_episode = Episode.objects.create(
            season=cls.season,
            number=3,
            title='Second Published Episode',
            content='<p>Published episode support content with second-keyword.</p>',
            status=Episode.Status.PUBLISHED,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )

        cls.alpha_title = MediaTitle.objects.create(
            title='SortCase Alpha',
            kind=MediaTitle.Kind.MOVIE,
            summary='Sort fixture alpha.',
            movie_content='<p>Sort alpha content.</p>',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )
        cls.recent_title = MediaTitle.objects.create(
            title='SortCase Recent',
            kind=MediaTitle.Kind.MOVIE,
            summary='Sort fixture recent.',
            movie_content='<p>Sort recent content.</p>',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )
        cls.published_title = MediaTitle.objects.create(
            title='SortCase Published',
            kind=MediaTitle.Kind.MOVIE,
            summary='Sort fixture published.',
            movie_content='<p>Sort published content.</p>',
            movie_content_status=MediaTitle.ContentStatus.PUBLISHED,
            created_by=cls.admin_user,
            updated_by=cls.admin_user,
        )

        now = timezone.now()
        MediaTitle.objects.filter(pk=cls.alpha_title.pk).update(
            updated_at=now - timedelta(days=3),
            published_at=now - timedelta(days=7),
        )
        MediaTitle.objects.filter(pk=cls.recent_title.pk).update(
            updated_at=now - timedelta(hours=1),
            published_at=now - timedelta(days=4),
        )
        MediaTitle.objects.filter(pk=cls.published_title.pk).update(
            updated_at=now - timedelta(days=2),
            published_at=now - timedelta(minutes=10),
        )

    def test_catalog_requires_login(self):
        response = self.client.get(reverse('support_library:catalog'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('support_library:catalog')}",
        )

    def test_normal_user_can_read_catalog_and_only_published_episode_links(self):
        self.client.force_login(self.normal_user)

        response = self.client.get(reverse('support_library:title-detail', kwargs={'slug': self.series.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The Pilot')
        self.assertNotContains(response, 'Draft Episode')

    def test_admin_can_access_management_list(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('support_library:manage-title-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Support Library')

    def test_normal_user_cannot_access_management_list(self):
        self.client.force_login(self.normal_user)

        response = self.client.get(reverse('support_library:manage-title-list'))

        self.assertEqual(response.status_code, 403)

    def test_catalog_search_filters_titles(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('support_library:catalog'), {'q': 'Black Mirror'})

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Black Mirror')
        self.assertNotContains(response, 'Arrival')

    def test_catalog_search_matches_episode_content(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('support_library:catalog'), {'q': 'pilot-keyword'})

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Friends')
        self.assertContains(response, '1 matching episode')

    def test_title_detail_search_filters_visible_episodes_by_text(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('support_library:title-detail', kwargs={'slug': self.series.slug}), {'q': 'second-keyword'})

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Second Published Episode')
        self.assertNotContains(response, 'The Pilot')
        self.assertNotContains(response, 'Draft Episode')

    def test_catalog_sort_recent_returns_most_recently_updated_title_first(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('support_library:catalog'), {'q': 'SortCase', 'sort': 'recent'})
        titles = list(response.context['titles'])

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(titles[0].title, 'SortCase Recent')

    def test_catalog_sort_published_returns_latest_published_title_first(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('support_library:catalog'), {'q': 'SortCase', 'sort': 'published'})
        titles = list(response.context['titles'])

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(titles[0].title, 'SortCase Published')

    def test_episode_detail_exposes_previous_and_next_published_episodes(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(
            reverse(
                'support_library:episode-detail',
                kwargs={
                    'slug': self.series.slug,
                    'season_number': self.season.number,
                    'episode_number': self.second_published_episode.number,
                },
            )
        )

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['previous_episode'].pk, self.published_episode.pk)
        self.assertIsNone(response.context['next_episode'])
