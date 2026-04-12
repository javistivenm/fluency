from django.conf import settings
from django.db import models
from django.utils import timezone


class DailyTask(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class UserDailyTaskStatus(models.Model):
    task = models.ForeignKey(DailyTask, on_delete=models.PROTECT, related_name='daily_statuses')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_task_statuses')
    task_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-task_date', 'task__sort_order', 'task__name']
        constraints = [
            models.UniqueConstraint(
                fields=['task', 'user', 'task_date'],
                name='unique_daily_task_status_per_user_and_day',
            ),
        ]

    def save(self, *args, **kwargs):
        if self.completed:
            if self.completed_at is None:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user} · {self.task} · {self.task_date}'
