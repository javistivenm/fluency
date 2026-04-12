from django.contrib import admin

from .models import DailyTask, UserDailyTaskStatus


@admin.register(DailyTask)
class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'sort_order', 'updated_at')
    list_filter = ('is_active',)
    ordering = ('sort_order', 'name')
    search_fields = ('name', 'description')


@admin.register(UserDailyTaskStatus)
class UserDailyTaskStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'task_date', 'completed', 'completed_at')
    list_filter = ('completed', 'task_date', 'task')
    search_fields = ('user__username', 'task__name')
    date_hierarchy = 'task_date'
