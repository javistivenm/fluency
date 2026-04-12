from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.signals import ADMIN_GROUP_NAME, USER_GROUP_NAME

from .forms import DailyTaskForm
from .models import DailyTask, UserDailyTaskStatus

User = get_user_model()


class DailyTaskModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='daily-task-model-user', password='StrongPassword123!')

    def test_user_daily_task_status_is_unique_per_user_task_and_date(self):
        # Arrange
        task = DailyTask.objects.create(name='Unique task', sort_order=1)
        current_date = timezone.localdate()
        UserDailyTaskStatus.objects.create(user=self.user, task=task, task_date=current_date, completed=True)

        # Act / Assert
        with self.assertRaises(IntegrityError):
            UserDailyTaskStatus.objects.create(user=self.user, task=task, task_date=current_date, completed=False)

    def test_completed_at_is_set_when_task_is_completed(self):
        # Arrange
        task = DailyTask.objects.create(name='Completed task', sort_order=1)
        status = UserDailyTaskStatus.objects.create(
            user=self.user,
            task=task,
            task_date=timezone.localdate(),
            completed=True,
        )

        # Act
        status.refresh_from_db()

        # Assert
        self.assertIsNotNone(status.completed_at)

    def test_completed_at_is_cleared_when_task_is_unchecked(self):
        # Arrange
        task = DailyTask.objects.create(name='Unchecked task', sort_order=1)
        status = UserDailyTaskStatus.objects.create(
            user=self.user,
            task=task,
            task_date=timezone.localdate(),
            completed=True,
        )

        # Act
        status.completed = False
        status.save()
        status.refresh_from_db()

        # Assert
        self.assertIsNone(status.completed_at)

    def test_daily_tasks_are_ordered_by_sort_order_and_name(self):
        # Arrange
        DailyTask.objects.create(name='Ordering Zulu', sort_order=202)
        DailyTask.objects.create(name='Ordering Alpha', sort_order=201)
        DailyTask.objects.create(name='Ordering Beta', sort_order=201)

        # Act
        ordered_names = list(
            DailyTask.objects.filter(name__startswith='Ordering ').values_list('name', flat=True)
        )

        # Assert
        self.assertEqual(ordered_names, ['Ordering Alpha', 'Ordering Beta', 'Ordering Zulu'])

    def test_history_survives_when_task_name_changes(self):
        # Arrange
        task = DailyTask.objects.create(name='Original name', sort_order=1)
        status = UserDailyTaskStatus.objects.create(
            user=self.user,
            task=task,
            task_date=timezone.localdate(),
            completed=True,
        )

        # Act
        task.name = 'Updated name'
        task.save()
        status.refresh_from_db()

        # Assert
        self.assertEqual(status.task.name, 'Updated name')


class DailyTaskFormTests(TestCase):
    def test_daily_task_form_accepts_valid_payload(self):
        # Arrange
        form = DailyTaskForm(
            data={
                'name': 'Unique speaking habit',
                'description': 'Five minutes of speaking practice.',
                'is_active': True,
                'sort_order': 1,
            }
        )

        # Act
        is_valid = form.is_valid()

        # Assert
        self.assertTrue(is_valid)

    def test_daily_task_form_requires_name(self):
        # Arrange
        form = DailyTaskForm(
            data={
                'name': '',
                'description': 'Missing name.',
                'is_active': True,
                'sort_order': 1,
            }
        )

        # Act
        is_valid = form.is_valid()

        # Assert
        self.assertFalse(is_valid)
        self.assertIn('name', form.errors)

    def test_daily_task_form_requires_sort_order(self):
        # Arrange
        form = DailyTaskForm(
            data={
                'name': 'Shadowing',
                'description': 'Repeat the target audio.',
                'is_active': True,
                'sort_order': '',
            }
        )

        # Act
        is_valid = form.is_valid()

        # Assert
        self.assertFalse(is_valid)
        self.assertIn('sort_order', form.errors)


class DailyTaskPermissionTests(TestCase):
    def test_admin_group_receives_daily_task_permissions(self):
        # Arrange
        admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)

        # Act / Assert
        self.assertTrue(admin_group.permissions.filter(codename='view_dailytask').exists())
        self.assertTrue(admin_group.permissions.filter(codename='add_dailytask').exists())
        self.assertTrue(admin_group.permissions.filter(codename='change_dailytask').exists())
        self.assertTrue(admin_group.permissions.filter(codename='view_userdailytaskstatus').exists())


class DailyTaskSeedDataTests(TestCase):
    def test_seed_tasks_exist_after_migrations(self):
        # Arrange / Act
        task_names = list(DailyTask.objects.values_list('name', flat=True))

        # Assert
        self.assertIn('Speaking alone', task_names)
        self.assertIn('TV Shows', task_names)
        self.assertEqual(len(task_names), 12)

    def test_seed_tasks_have_expected_order(self):
        # Arrange / Act
        ordered_names = list(DailyTask.objects.order_by('sort_order').values_list('name', flat=True)[:3])

        # Assert
        self.assertEqual(ordered_names, ['Speaking alone', 'Shadowing', 'Phrase memorization'])


class DailyTaskViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
        cls.user_group = Group.objects.get(name=USER_GROUP_NAME)
        cls.admin_user = User.objects.create_user(username='daily-admin', password='StrongPassword123!')
        cls.admin_user.groups.add(cls.admin_group)
        cls.normal_user = User.objects.create_user(username='daily-user', password='StrongPassword123!')
        cls.normal_user.groups.add(cls.user_group)

        cls.active_task = DailyTask.objects.create(
            name='Daily active task',
            description='Visible active task.',
            is_active=True,
            sort_order=100,
        )
        cls.second_active_task = DailyTask.objects.create(
            name='Daily second active task',
            description='Second active task.',
            is_active=True,
            sort_order=101,
        )
        cls.inactive_task = DailyTask.objects.create(
            name='Daily inactive task',
            description='Should stay hidden.',
            is_active=False,
            sort_order=102,
        )

    def test_daily_tasks_page_requires_login(self):
        # Arrange / Act
        response = self.client.get(reverse('daily_tasks:today'))

        # Assert
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('daily_tasks:today')}",
        )

    def test_normal_user_sees_only_active_tasks(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('daily_tasks:today'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daily active task')
        self.assertContains(response, 'Daily second active task')
        self.assertNotContains(response, 'Daily inactive task')

    def test_toggle_creates_status_for_today_when_missing(self):
        # Arrange
        self.client.force_login(self.normal_user)
        current_date = timezone.localdate()

        # Act
        response = self.client.post(
            reverse('daily_tasks:toggle-task-status', kwargs={'task_id': self.active_task.pk}),
            {'completed': 'true'},
        )

        # Assert
        self.assertRedirects(response, reverse('daily_tasks:today'))
        self.assertTrue(
            UserDailyTaskStatus.objects.filter(
                user=self.normal_user,
                task=self.active_task,
                task_date=current_date,
                completed=True,
            ).exists()
        )

    def test_toggle_unmarks_task_when_already_completed(self):
        # Arrange
        current_date = timezone.localdate()
        UserDailyTaskStatus.objects.create(
            user=self.normal_user,
            task=self.active_task,
            task_date=current_date,
            completed=True,
        )
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.post(
            reverse('daily_tasks:toggle-task-status', kwargs={'task_id': self.active_task.pk}),
            {'completed': 'false'},
        )

        # Assert
        self.assertRedirects(response, reverse('daily_tasks:today'))
        status = UserDailyTaskStatus.objects.get(user=self.normal_user, task=self.active_task, task_date=current_date)
        self.assertFalse(status.completed)
        self.assertIsNone(status.completed_at)

    def test_task_completion_today_does_not_affect_other_dates(self):
        # Arrange
        yesterday = timezone.localdate() - timedelta(days=1)
        UserDailyTaskStatus.objects.create(
            user=self.normal_user,
            task=self.active_task,
            task_date=yesterday,
            completed=False,
        )
        self.client.force_login(self.normal_user)

        # Act
        self.client.post(
            reverse('daily_tasks:toggle-task-status', kwargs={'task_id': self.active_task.pk}),
            {'completed': 'true'},
        )

        # Assert
        yesterday_status = UserDailyTaskStatus.objects.get(user=self.normal_user, task=self.active_task, task_date=yesterday)
        today_status = UserDailyTaskStatus.objects.get(
            user=self.normal_user,
            task=self.active_task,
            task_date=timezone.localdate(),
        )
        self.assertFalse(yesterday_status.completed)
        self.assertTrue(today_status.completed)

    def test_toggle_returns_404_for_inactive_task(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.post(
            reverse('daily_tasks:toggle-task-status', kwargs={'task_id': self.inactive_task.pk}),
            {'completed': 'true'},
        )

        # Assert
        self.assertEqual(response.status_code, 404)

    def test_admin_can_access_task_management_list(self):
        # Arrange
        self.client.force_login(self.admin_user)

        # Act
        response = self.client.get(reverse('daily_tasks:manage-task-list'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Daily Tasks')

    def test_normal_user_cannot_access_task_management_list(self):
        # Arrange
        self.client.force_login(self.normal_user)

        # Act
        response = self.client.get(reverse('daily_tasks:manage-task-list'))

        # Assert
        self.assertEqual(response.status_code, 403)

    def test_management_list_filters_by_state(self):
        # Arrange
        self.client.force_login(self.admin_user)

        # Act
        response = self.client.get(reverse('daily_tasks:manage-task-list'), {'q': 'Daily', 'state': 'inactive'})

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Daily inactive task')
        self.assertNotContains(response, 'Daily active task')

    def test_management_toggle_active_updates_task_state(self):
        # Arrange
        self.client.force_login(self.admin_user)

        # Act
        response = self.client.post(reverse('daily_tasks:manage-task-toggle-active', kwargs={'pk': self.active_task.pk}))

        # Assert
        self.assertRedirects(response, reverse('daily_tasks:manage-task-list'))
        self.active_task.refresh_from_db()
        self.assertFalse(self.active_task.is_active)
