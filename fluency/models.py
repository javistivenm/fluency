from django.core.exceptions import ValidationError
from django.db import models


class Level(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'code']

    def __str__(self):
        return self.code


class OutputFormat(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ExerciseType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_output_format = models.ForeignKey(
        OutputFormat,
        on_delete=models.SET_NULL,
        related_name='default_for_types',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ConstraintType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Constraint(models.Model):
    constraint_type = models.ForeignKey(
        ConstraintType,
        on_delete=models.PROTECT,
        related_name='constraints',
    )
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='constraints')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['level__sort_order', 'name']
        constraints = [
            models.UniqueConstraint(fields=['level', 'slug'], name='unique_constraint_per_level'),
        ]

    def __str__(self):
        return f'{self.level.code} · {self.name}'


class Topic(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Exercise(models.Model):
    title = models.CharField(max_length=200)
    instructions = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='exercises')
    exercise_type = models.ForeignKey(
        ExerciseType,
        on_delete=models.PROTECT,
        related_name='exercises',
    )
    topic = models.ForeignKey(Topic, on_delete=models.PROTECT, related_name='exercises')
    output_format = models.ForeignKey(
        OutputFormat,
        on_delete=models.PROTECT,
        related_name='exercises',
    )
    pedagogical_goal = models.CharField(max_length=255)
    grammar_focus = models.CharField(max_length=100, blank=True)
    writing_function = models.CharField(max_length=100, blank=True)
    difficulty_score = models.PositiveSmallIntegerField(default=1)
    word_count_min = models.PositiveSmallIntegerField()
    word_count_max = models.PositiveSmallIntegerField()
    estimated_time_minutes = models.PositiveSmallIntegerField()
    tone = models.CharField(max_length=50, blank=True)
    rotation_group = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    constraints = models.ManyToManyField(
        Constraint,
        through='ExerciseConstraint',
        related_name='exercises',
        blank=True,
    )

    class Meta:
        ordering = ['level__sort_order', 'exercise_type__name', 'title']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(word_count_max__gte=models.F('word_count_min')),
                name='exercise_word_count_range_valid',
            ),
        ]

    def clean(self):
        if self.word_count_max < self.word_count_min:
            raise ValidationError({'word_count_max': 'word_count_max must be greater than or equal to word_count_min.'})

    def __str__(self):
        return self.title


class ExerciseConstraint(models.Model):
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='exercise_constraints',
    )
    constraint = models.ForeignKey(
        Constraint,
        on_delete=models.CASCADE,
        related_name='exercise_constraints',
    )

    class Meta:
        ordering = ['exercise', 'constraint']
        constraints = [
            models.UniqueConstraint(
                fields=['exercise', 'constraint'],
                name='unique_exercise_constraint',
            ),
        ]

    def __str__(self):
        return f'{self.exercise} · {self.constraint.name}'


class DailyChallenge(models.Model):
    challenge_date = models.DateField()
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='daily_challenges')
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name='daily_challenges',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-challenge_date', 'level__sort_order']
        constraints = [
            models.UniqueConstraint(
                fields=['challenge_date', 'level'],
                name='unique_daily_challenge_per_level',
            ),
        ]

    def __str__(self):
        return f'{self.challenge_date} · {self.level.code} · {self.exercise.title}'
