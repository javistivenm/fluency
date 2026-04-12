from django import forms

from .models import DailyTask


class DailyTaskForm(forms.ModelForm):
    class Meta:
        model = DailyTask
        fields = ('name', 'description', 'is_active', 'sort_order')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Example: Speaking alone'
        self.fields['description'].widget.attrs['placeholder'] = 'Optional short note about how the task should be done.'
        self.fields['sort_order'].help_text = 'Lower numbers appear first in the daily list.'
