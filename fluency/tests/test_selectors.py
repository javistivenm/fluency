from datetime import date, timedelta

from django.test import TestCase

from fluency.models import DailyChallenge, Exercise, ExerciseType, Level, OutputFormat, Topic
from fluency.selectors import get_or_create_daily_challenge


class DailyChallengeSelectorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.level = Level.objects.create(code='T2', name='Selector Level', description='Level for selector tests', sort_order=98)
        cls.quick_response = ExerciseType.objects.get(slug='quick-response')
        cls.description = ExerciseType.objects.get(slug='description')
        cls.output_format = OutputFormat.objects.get(slug='three-sentences')
        cls.topic = Topic.objects.get(slug='daily-life')

    def _create_exercise(self, title, exercise_type):
        return Exercise.objects.create(
            title=title,
            instructions='Write your response.',
            level=self.level,
            exercise_type=exercise_type,
            topic=self.topic,
            output_format=self.output_format,
            pedagogical_goal='Build confidence through daily writing.',
            grammar_focus='present simple',
            writing_function='describe',
            difficulty_score=1,
            word_count_min=20,
            word_count_max=40,
            estimated_time_minutes=5,
            tone='personal',
            rotation_group='daily_selector',
        )

    def test_reuses_existing_daily_challenge(self):
        exercise = self._create_exercise('Existing challenge', self.quick_response)
        challenge_date = date(2026, 4, 6)
        challenge = DailyChallenge.objects.create(
            challenge_date=challenge_date,
            level=self.level,
            exercise=exercise,
        )

        selected = get_or_create_daily_challenge(self.level, target_date=challenge_date)

        self.assertEqual(selected.pk, challenge.pk)

    def test_prioritizes_exercise_type_for_the_day(self):
        self._create_exercise('Description fallback', self.description)
        quick_response_exercise = self._create_exercise('Quick response match', self.quick_response)

        selected = get_or_create_daily_challenge(self.level, target_date=date(2026, 4, 6))

        self.assertEqual(selected.exercise.pk, quick_response_exercise.pk)

    def test_falls_back_when_daily_type_is_missing(self):
        description_exercise = self._create_exercise('Description only', self.description)

        selected = get_or_create_daily_challenge(self.level, target_date=date(2026, 4, 6))

        self.assertEqual(selected.exercise.pk, description_exercise.pk)

    def test_avoids_recent_exercises_when_alternatives_exist(self):
        recent_exercise = self._create_exercise('Recent quick response', self.quick_response)
        fresh_exercise = self._create_exercise('Fresh quick response', self.quick_response)
        target_date = date(2026, 4, 6)
        DailyChallenge.objects.create(
            challenge_date=target_date - timedelta(days=1),
            level=self.level,
            exercise=recent_exercise,
        )

        selected = get_or_create_daily_challenge(self.level, target_date=target_date)

        self.assertEqual(selected.exercise.pk, fresh_exercise.pk)
