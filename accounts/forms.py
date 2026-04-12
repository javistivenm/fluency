from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group

from .signals import ADMIN_GROUP_NAME, USER_GROUP_NAME

User = get_user_model()


class FluencyAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username')


class UserGroupMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(
            name__in=[ADMIN_GROUP_NAME, USER_GROUP_NAME],
        ).order_by('name')
        if self.instance.pk:
            self.fields['group'].initial = self.instance.groups.order_by('name').first()

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.set([self.cleaned_data['group']])
        else:
            self._selected_group = self.cleaned_data['group']
        return user

    def save_m2m(self):
        super().save_m2m()
        if hasattr(self, '_selected_group'):
            self.instance.groups.set([self._selected_group])


class CustomUserCreationForm(UserGroupMixin, UserCreationForm):
    group = forms.ModelChoiceField(
        label='Role',
        queryset=Group.objects.none(),
        empty_label=None,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CustomUserChangeForm(UserGroupMixin, forms.ModelForm):
    group = forms.ModelChoiceField(
        label='Role',
        queryset=Group.objects.none(),
        empty_label=None,
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')
