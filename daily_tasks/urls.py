from django.urls import path

from .views import (
    DailyTasksTodayView,
    ManageDailyTaskCreateView,
    ManageDailyTaskListView,
    ManageDailyTaskUpdateView,
    ToggleDailyTaskActiveView,
    ToggleDailyTaskStatusView,
)

app_name = 'daily_tasks'

urlpatterns = [
    path('', DailyTasksTodayView.as_view(), name='today'),
    path('toggle/<int:task_id>/', ToggleDailyTaskStatusView.as_view(), name='toggle-task-status'),
    path('manage/', ManageDailyTaskListView.as_view(), name='manage-task-list'),
    path('manage/create/', ManageDailyTaskCreateView.as_view(), name='manage-task-create'),
    path('manage/<int:pk>/edit/', ManageDailyTaskUpdateView.as_view(), name='manage-task-update'),
    path('manage/<int:pk>/toggle-active/', ToggleDailyTaskActiveView.as_view(), name='manage-task-toggle-active'),
]
