from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import Episode, MediaTitle, Season


class MediaTitleForm(forms.ModelForm):
    class Meta:
        model = MediaTitle
        fields = ('title', 'kind', 'summary', 'is_active', 'movie_content_status', 'movie_content')
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4}),
            'movie_content': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Example: Castlevania: Nocturne'
        self.fields['summary'].widget.attrs['placeholder'] = 'Write a short description so learners know what they will find here.'
        self.fields['kind'].help_text = 'Use Series for content organized by seasons and episodes. Use Movie for one single support text.'
        self.fields['movie_content'].required = False
        self.fields['movie_content_status'].label = 'Movie content visibility'
        self.fields['movie_content_status'].help_text = 'This applies only when the title is a movie.'
        self.fields['movie_content'].help_text = 'Use this only for movie entries. Series content belongs in episodes.'


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ('number', 'title', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Optional season label'


class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ('number', 'title', 'status', 'is_active', 'content')
        widgets = {
            'content': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['placeholder'] = 'Example: Episode 1'
        self.fields['status'].help_text = 'Keep draft while you work. Publish when learners are allowed to read it.'
