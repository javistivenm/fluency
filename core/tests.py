from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CoreViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='dashboard-user', password='StrongPassword123!')

    def test_root_redirects_to_login_for_anonymous_users(self):
        response = self.client.get(reverse('core:root'))

        self.assertRedirects(response, reverse('accounts:login'))

    def test_root_redirects_to_dashboard_for_authenticated_users(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('core:root'))

        self.assertRedirects(response, reverse('core:dashboard'))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('core:dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('core:dashboard')}",
        )

    def test_dashboard_renders_module_links(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('core:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Writing Practice Daily')
        self.assertContains(response, 'Support Library')
        self.assertContains(response, 'Daily Tasks')
