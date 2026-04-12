from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CustomUserChangeForm, CustomUserCreationForm, FluencyAuthenticationForm

User = get_user_model()


class LoginAndPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class LoginView(auth_views.LoginView):
    authentication_form = FluencyAuthenticationForm
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class UserListView(LoginAndPermissionRequiredMixin, ListView):
    model = User
    context_object_name = 'users'
    ordering = ('username',)
    permission_required = 'accounts.view_user'
    template_name = 'accounts/user_list.html'

    def get_queryset(self):
        return User.objects.prefetch_related('groups').order_by(*self.ordering)


class UserCreateView(LoginAndPermissionRequiredMixin, CreateView):
    form_class = CustomUserCreationForm
    permission_required = 'accounts.add_user'
    success_url = reverse_lazy('accounts:user-list')
    template_name = 'accounts/user_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User created successfully.')
        return response


class UserUpdateView(LoginAndPermissionRequiredMixin, UpdateView):
    form_class = CustomUserChangeForm
    model = User
    permission_required = 'accounts.change_user'
    success_url = reverse_lazy('accounts:user-list')
    template_name = 'accounts/user_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'User updated successfully.')
        return response


class UserDeleteView(LoginAndPermissionRequiredMixin, DeleteView):
    model = User
    permission_required = 'accounts.delete_user'
    success_url = reverse_lazy('accounts:user-list')
    template_name = 'accounts/user_confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'User deleted successfully.')
        return super().form_valid(form)
