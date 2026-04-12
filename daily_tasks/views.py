from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import DailyTaskForm
from .models import DailyTask, UserDailyTaskStatus


class DailyTasksTodayView(LoginRequiredMixin, TemplateView):
    template_name = 'daily_tasks/today.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.localdate()
        tasks = list(DailyTask.objects.filter(is_active=True).order_by('sort_order', 'name'))
        statuses = {
            status.task_id: status
            for status in UserDailyTaskStatus.objects.filter(
                user=self.request.user,
                task_date=current_date,
                task__in=tasks,
            )
        }

        task_rows = []
        for task in tasks:
            status = statuses.get(task.id)
            task_rows.append(
                {
                    'task': task,
                    'status': status,
                    'is_completed': bool(status and status.completed),
                }
            )

        completed_count = sum(1 for task_row in task_rows if task_row['is_completed'])
        total_count = len(task_rows)
        progress_percentage = int((completed_count / total_count) * 100) if total_count else 0

        context.update(
            {
                'current_date': current_date,
                'task_rows': task_rows,
                'completed_count': completed_count,
                'total_count': total_count,
                'progress_percentage': progress_percentage,
            }
        )
        return context


class ToggleDailyTaskStatusView(LoginRequiredMixin, View):
    def post(self, request, task_id):
        task = get_object_or_404(DailyTask, pk=task_id, is_active=True)
        current_date = timezone.localdate()
        status, _ = UserDailyTaskStatus.objects.get_or_create(
            user=request.user,
            task=task,
            task_date=current_date,
            defaults={'completed': False},
        )

        completed = request.POST.get('completed')
        if completed is None:
            status.completed = not status.completed
        else:
            status.completed = completed == 'true'
        status.save()

        if status.completed:
            messages.success(request, f'"{task.name}" marked as completed for today.')
        else:
            messages.info(request, f'"{task.name}" marked as pending again.')
        return redirect('daily_tasks:today')


class DailyTasksManageMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class ManageDailyTaskListView(DailyTasksManageMixin, ListView):
    context_object_name = 'tasks'
    model = DailyTask
    permission_required = 'daily_tasks.view_dailytask'
    template_name = 'daily_tasks/manage/task_list.html'

    def get_queryset(self):
        queryset = DailyTask.objects.annotate(
            completed_today_count=Count(
                'daily_statuses',
                filter=Q(
                    daily_statuses__task_date=timezone.localdate(),
                    daily_statuses__completed=True,
                ),
                distinct=True,
            )
        )

        query = self.request.GET.get('q', '').strip()
        state = self.request.GET.get('state', '').strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if state == 'active':
            queryset = queryset.filter(is_active=True)
        elif state == 'inactive':
            queryset = queryset.filter(is_active=False)
        return queryset.order_by('sort_order', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'current_query': self.request.GET.get('q', '').strip(),
                'current_state': self.request.GET.get('state', '').strip(),
                'results_count': context['tasks'].count(),
            }
        )
        return context


class ManageDailyTaskCreateView(DailyTasksManageMixin, CreateView):
    form_class = DailyTaskForm
    permission_required = 'daily_tasks.add_dailytask'
    success_url = reverse_lazy('daily_tasks:manage-task-list')
    template_name = 'daily_tasks/manage/task_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Daily task created successfully.')
        return response


class ManageDailyTaskUpdateView(DailyTasksManageMixin, UpdateView):
    form_class = DailyTaskForm
    model = DailyTask
    permission_required = 'daily_tasks.change_dailytask'
    success_url = reverse_lazy('daily_tasks:manage-task-list')
    template_name = 'daily_tasks/manage/task_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Daily task updated successfully.')
        return response


class ToggleDailyTaskActiveView(DailyTasksManageMixin, View):
    permission_required = 'daily_tasks.change_dailytask'

    def post(self, request, pk):
        task = get_object_or_404(DailyTask, pk=pk)
        task.is_active = not task.is_active
        task.save(update_fields=['is_active', 'updated_at'])
        if task.is_active:
            messages.success(request, f'"{task.name}" is active again.')
        else:
            messages.info(request, f'"{task.name}" was deactivated.')
        return redirect('daily_tasks:manage-task-list')
