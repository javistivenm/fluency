from datetime import timedelta
import random

from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import DailyChallenge, Exercise, Level

DAILY_TYPE_ROTATION = {
    0: 'quick-response',
    1: 'opinion',
    2: 'description',
    3: 'rewrite-challenge',
    4: 'compare-and-choose',
    5: 'storytelling',
    6: 'reflection',
}

RECENT_CHALLENGE_WINDOW_DAYS = 14


def get_selected_level(request):
    level_code = request.session.get('selected_level_code')
    if not level_code:
        return None

    return Level.objects.filter(code=level_code, is_active=True).first()


def get_daily_type_slug(target_date):
    return DAILY_TYPE_ROTATION[target_date.weekday()]


def get_or_create_daily_challenge(level, target_date=None):
    target_date = target_date or timezone.localdate()
    challenge = DailyChallenge.objects.select_related(
        'exercise',
        'exercise__exercise_type',
        'exercise__topic',
        'exercise__output_format',
        'level',
    ).filter(challenge_date=target_date, level=level).first()

    if challenge is not None:
        return challenge

    exercise = _select_exercise(level, target_date)
    if exercise is None:
        return None

    try:
        with transaction.atomic():
            return DailyChallenge.objects.create(
                challenge_date=target_date,
                level=level,
                exercise=exercise,
            )
    except IntegrityError:
        return DailyChallenge.objects.select_related(
            'exercise',
            'exercise__exercise_type',
            'exercise__topic',
            'exercise__output_format',
            'level',
        ).get(challenge_date=target_date, level=level)


def _select_exercise(level, target_date):
    preferred_type_slug = get_daily_type_slug(target_date)
    recent_exercise_ids = _recent_exercise_ids(level, target_date)

    preferred_queryset = Exercise.objects.filter(
        level=level,
        is_active=True,
        exercise_type__slug=preferred_type_slug,
    ).exclude(pk__in=recent_exercise_ids)
    exercise = _pick_seeded_choice(preferred_queryset, level.code, target_date)
    if exercise is not None:
        return exercise

    fallback_queryset = Exercise.objects.filter(level=level, is_active=True).exclude(pk__in=recent_exercise_ids)
    exercise = _pick_seeded_choice(fallback_queryset, level.code, target_date)
    if exercise is not None:
        return exercise

    final_queryset = Exercise.objects.filter(level=level, is_active=True)
    return _pick_seeded_choice(final_queryset, level.code, target_date)


def _recent_exercise_ids(level, target_date):
    recent_start = target_date - timedelta(days=RECENT_CHALLENGE_WINDOW_DAYS)
    return DailyChallenge.objects.filter(
        level=level,
        challenge_date__gte=recent_start,
        challenge_date__lt=target_date,
    ).values_list('exercise_id', flat=True)


def _pick_seeded_choice(queryset, level_code, target_date):
    exercises = list(queryset.select_related('exercise_type', 'topic', 'output_format').order_by('pk'))
    if not exercises:
        return None

    seeded_random = random.Random(f'{level_code}:{target_date.isoformat()}:{len(exercises)}')
    return seeded_random.choice(exercises)
