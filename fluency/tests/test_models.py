from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from fluency.models import Constraint, ConstraintType, DailyChallenge, Exercise, ExerciseConstraint, ExerciseType, Level, OutputFormat, Topic


class FluencyModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.level = Level.objects.create(code='T1', name='Test Level', description='Level for tests', sort_order=99)
        cls.output_format = OutputFormat.objects.create(
            name='Test paragraph',
            slug='test-paragraph',
            description='Output format for tests',
        )
        cls.exercise_type = ExerciseType.objects.create(
            name='Test Type',
            slug='test-type',
            description='Exercise type for tests',
            default_output_format=cls.output_format,
        )
        cls.topic = Topic.objects.create(
            name='Test Topic',
            slug='test-topic',
            description='Topic for tests',
        )
        cls.constraint_type = ConstraintType.objects.create(
            name='Test Constraint Type',
            slug='test-constraint-type',
            description='Constraint type for tests',
        )
        cls.constraint = Constraint.objects.create(
            constraint_type=cls.constraint_type,
            level=cls.level,
            name='Write five sentences',
            slug='write-five-sentences',
            description='Constraint for tests',
        )

    def _create_exercise(self, title='Test exercise'):
        return Exercise.objects.create(
            title=title,
            instructions='Write a short answer.',
            level=self.level,
            exercise_type=self.exercise_type,
            topic=self.topic,
            output_format=self.output_format,
            pedagogical_goal='Practice basic structure.',
            grammar_focus='present simple',
            writing_function='describe',
            difficulty_score=1,
            word_count_min=20,
            word_count_max=40,
            estimated_time_minutes=5,
            tone='neutral',
            rotation_group='daily_test',
        )

    def test_exercise_full_clean_rejects_invalid_word_range(self):
        exercise = Exercise(
            title='Invalid range',
            instructions='Write a short answer.',
            level=self.level,
            exercise_type=self.exercise_type,
            topic=self.topic,
            output_format=self.output_format,
            pedagogical_goal='Practice basic structure.',
            grammar_focus='present simple',
            writing_function='describe',
            difficulty_score=1,
            word_count_min=50,
            word_count_max=20,
            estimated_time_minutes=5,
        )

        with self.assertRaises(ValidationError):
            exercise.full_clean()

    def test_daily_challenge_is_unique_per_level_and_date(self):
        first_exercise = self._create_exercise('First exercise')
        second_exercise = self._create_exercise('Second exercise')
        challenge_date = date(2026, 4, 4)

        DailyChallenge.objects.create(
            challenge_date=challenge_date,
            level=self.level,
            exercise=first_exercise,
        )

        with self.assertRaises(IntegrityError):
            DailyChallenge.objects.create(
                challenge_date=challenge_date,
                level=self.level,
                exercise=second_exercise,
            )

    def test_exercise_constraint_is_unique(self):
        exercise = self._create_exercise()
        ExerciseConstraint.objects.create(exercise=exercise, constraint=self.constraint)

        with self.assertRaises(IntegrityError):
            ExerciseConstraint.objects.create(exercise=exercise, constraint=self.constraint)
