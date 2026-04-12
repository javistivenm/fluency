from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from fluency.models import Exercise, ExerciseType, Level, OutputFormat, Topic

User = get_user_model()


class FluencyViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.quick_response = ExerciseType.objects.get(slug='quick-response')
        cls.output_format = OutputFormat.objects.get(slug='three-sentences')
        cls.topic = Topic.objects.get(slug='daily-life')
        cls.level = Level.objects.create(code='T3', name='View Level', description='Level for views', sort_order=97)
        Exercise.objects.create(
            title='View test challenge',
            instructions='Write three sentences about your day.',
            level=cls.level,
            exercise_type=cls.quick_response,
            topic=cls.topic,
            output_format=cls.output_format,
            pedagogical_goal='Build a daily writing habit.',
            grammar_focus='present simple',
            writing_function='describe',
            difficulty_score=1,
            word_count_min=20,
            word_count_max=40,
            estimated_time_minutes=5,
            tone='personal',
            rotation_group='daily_views',
        )
        cls.user = User.objects.create_user(
            username='learner',
            password='StrongPassword123!',
        )

    def test_home_page_renders(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('fluency:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Practice English writing with one focused challenge every day.')

    def test_home_page_requires_login(self):
        response = self.client.get(reverse('fluency:home'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('fluency:home')}",
        )

    def test_set_level_stores_selection_in_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('fluency:set-level'), {'level_code': 'A2'})

        self.assertRedirects(response, reverse('fluency:daily-challenge'))
        self.assertEqual(self.client.session['selected_level_code'], 'A2')

    def test_daily_challenge_redirects_without_level(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('fluency:daily-challenge'))

        self.assertRedirects(response, reverse('fluency:home'))

    def test_daily_challenge_requires_login(self):
        response = self.client.get(reverse('fluency:daily-challenge'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('fluency:daily-challenge')}",
        )

    def test_daily_challenge_renders_for_selected_level(self):
        self.client.force_login(self.user)
        session = self.client.session
        session['selected_level_code'] = self.level.code
        session.save()

        response = self.client.get(reverse('fluency:daily-challenge'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Today\'s writing prompt for')
        self.assertContains(response, 'View test challenge')
