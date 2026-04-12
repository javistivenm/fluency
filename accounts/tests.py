from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .signals import ADMIN_GROUP_NAME, USER_GROUP_NAME

User = get_user_model()


class AccountsSetupTests(TestCase):
    def test_default_groups_are_created(self):
        self.assertTrue(Group.objects.filter(name=ADMIN_GROUP_NAME).exists())
        self.assertTrue(Group.objects.filter(name=USER_GROUP_NAME).exists())

    def test_admin_group_receives_user_management_permissions(self):
        admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)

        self.assertTrue(admin_group.permissions.filter(codename='add_user').exists())
        self.assertTrue(admin_group.permissions.filter(codename='change_user').exists())
        self.assertTrue(admin_group.permissions.filter(codename='delete_user').exists())
        self.assertTrue(admin_group.permissions.filter(codename='view_user').exists())


class AccountsAccessTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_group = Group.objects.get(name=ADMIN_GROUP_NAME)
        cls.user_group = Group.objects.get(name=USER_GROUP_NAME)

        cls.admin_user = User.objects.create_user(username='manager', password='StrongPassword123!')
        cls.admin_user.groups.add(cls.admin_group)

        cls.normal_user = User.objects.create_user(username='student', password='StrongPassword123!')
        cls.normal_user.groups.add(cls.user_group)

    def test_user_list_requires_login(self):
        response = self.client.get(reverse('accounts:user-list'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:user-list')}",
        )

    def test_normal_user_cannot_access_user_list(self):
        self.client.force_login(self.normal_user)

        response = self.client.get(reverse('accounts:user-list'))

        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_access_user_list(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('accounts:user-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Users')
