from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class MediaTitle(models.Model):
    class Kind(models.TextChoices):
        SERIES = 'series', 'Series'
        MOVIE = 'movie', 'Movie'

    class ContentStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    summary = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    movie_content = models.TextField(blank=True)
    movie_content_status = models.CharField(
        max_length=10,
        choices=ContentStatus.choices,
        default=ContentStatus.DRAFT,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_support_titles',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='updated_support_titles',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def clean(self):
        movie_content = (self.movie_content or '').strip()
        if self.kind == self.Kind.MOVIE and self.movie_content_status == self.ContentStatus.PUBLISHED and not movie_content:
            raise ValidationError({'movie_content': 'Published movie entries require support content.'})
        if self.kind == self.Kind.SERIES and movie_content:
            raise ValidationError({'movie_content': 'Series support content must be stored per episode.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.kind == self.Kind.SERIES:
            self.movie_content = ''
            self.movie_content_status = self.ContentStatus.DRAFT
            self.published_at = None
        elif self.movie_content_status == self.ContentStatus.PUBLISHED:
            if self.published_at is None:
                self.published_at = timezone.now()
        else:
            self.published_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Season(models.Model):
    media_title = models.ForeignKey(MediaTitle, on_delete=models.CASCADE, related_name='seasons')
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['media_title__title', 'number']
        constraints = [
            models.UniqueConstraint(fields=['media_title', 'number'], name='unique_season_per_title'),
        ]

    def clean(self):
        if not self.media_title_id:
            return
        if self.media_title.kind != MediaTitle.Kind.SERIES:
            raise ValidationError({'media_title': 'Seasons can only be created for series.'})

    def __str__(self):
        return f'{self.media_title.title} · Season {self.number}'


class Episode(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_support_episodes',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='updated_support_episodes',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['season__media_title__title', 'season__number', 'number']
        constraints = [
            models.UniqueConstraint(fields=['season', 'number'], name='unique_episode_per_season'),
        ]

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED:
            if self.published_at is None:
                self.published_at = timezone.now()
        else:
            self.published_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.season.media_title.title} · S{self.season.number}E{self.number} · {self.title}'
