from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count, DateTimeField, F, IntegerField, Max, Prefetch, Q, Value
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EpisodeForm, MediaTitleForm, SeasonForm
from .models import Episode, MediaTitle, Season


def can_manage_support_library(user):
    return user.has_perm('support_library.change_mediatitle')


def annotate_support_library_titles(queryset, is_manager):
    visible_season_filter = Q(seasons__is_active=True)
    visible_episode_filter = Q(seasons__episodes__is_active=True, seasons__is_active=True)
    visible_published_episode_filter = visible_episode_filter & Q(seasons__episodes__status=Episode.Status.PUBLISHED)

    seasons_filter = Q() if is_manager else visible_season_filter
    episodes_filter = Q() if is_manager else visible_episode_filter
    published_episodes_filter = Q(seasons__episodes__status=Episode.Status.PUBLISHED) if is_manager else visible_published_episode_filter

    queryset = queryset.annotate(
        seasons_count=Count('seasons', filter=seasons_filter, distinct=True),
        episodes_count=Count('seasons__episodes', filter=episodes_filter, distinct=True),
        published_episodes_count=Count('seasons__episodes', filter=published_episodes_filter, distinct=True),
        latest_episode_publication_at=Max('seasons__episodes__published_at', filter=published_episodes_filter),
    )
    return queryset.annotate(
        latest_publication_at=Coalesce(
            'published_at',
            'latest_episode_publication_at',
            output_field=DateTimeField(),
        ),
    )


def apply_support_library_sort(queryset, sort_value):
    if sort_value == 'recent':
        return queryset.order_by(F('updated_at').desc(nulls_last=True), 'title')
    if sort_value == 'published':
        return queryset.order_by(F('latest_publication_at').desc(nulls_last=True), 'title')
    return queryset.order_by('title')


class SupportLibraryCatalogView(LoginRequiredMixin, ListView):
    context_object_name = 'titles'
    model = MediaTitle
    template_name = 'support_library/catalog.html'

    def get_queryset(self):
        is_manager = can_manage_support_library(self.request.user)
        queryset = annotate_support_library_titles(MediaTitle.objects.all(), is_manager)
        if not is_manager:
            queryset = queryset.filter(is_active=True)

        query = self.request.GET.get('q', '').strip()
        kind = self.request.GET.get('kind', '').strip()
        sort = self.request.GET.get('sort', 'alpha').strip()
        if query:
            title_query = Q(title__icontains=query) | Q(summary__icontains=query)
            if is_manager:
                movie_query = Q(movie_content__icontains=query)
                episode_query = Q(seasons__episodes__title__icontains=query) | Q(seasons__episodes__content__icontains=query)
                matched_episode_filter = Q(seasons__episodes__title__icontains=query) | Q(seasons__episodes__content__icontains=query)
            else:
                movie_query = Q(movie_content_status=MediaTitle.ContentStatus.PUBLISHED, movie_content__icontains=query)
                episode_query = (
                    Q(seasons__episodes__title__icontains=query) | Q(seasons__episodes__content__icontains=query)
                ) & Q(
                    seasons__episodes__status=Episode.Status.PUBLISHED,
                    seasons__episodes__is_active=True,
                    seasons__is_active=True,
                )
                matched_episode_filter = (
                    Q(seasons__episodes__title__icontains=query) | Q(seasons__episodes__content__icontains=query)
                ) & Q(
                    seasons__episodes__status=Episode.Status.PUBLISHED,
                    seasons__episodes__is_active=True,
                    seasons__is_active=True,
                )
            queryset = queryset.annotate(
                matched_episode_count=Count('seasons__episodes', filter=matched_episode_filter, distinct=True),
            ).filter(title_query | movie_query | episode_query).distinct()
        else:
            queryset = queryset.annotate(matched_episode_count=Value(0, output_field=IntegerField()))
        if kind in {MediaTitle.Kind.SERIES, MediaTitle.Kind.MOVIE}:
            queryset = queryset.filter(kind=kind)

        return apply_support_library_sort(queryset, sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'current_query': self.request.GET.get('q', '').strip(),
                'current_kind': self.request.GET.get('kind', '').strip(),
                'current_sort': self.request.GET.get('sort', 'alpha').strip(),
                'results_count': context['titles'].count(),
            }
        )
        return context


class SupportLibraryTitleDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'media_title'
    model = MediaTitle
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'support_library/title_detail.html'

    def get_queryset(self):
        queryset = MediaTitle.objects.all()
        if can_manage_support_library(self.request.user):
            return queryset
        return queryset.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_manager = can_manage_support_library(self.request.user)
        episode_queryset = Episode.objects.order_by('number')
        season_queryset = Season.objects.order_by('number')
        episode_query = self.request.GET.get('q', '').strip()
        if not is_manager:
            episode_queryset = episode_queryset.filter(is_active=True, status=Episode.Status.PUBLISHED)
            season_queryset = season_queryset.filter(is_active=True)
        if episode_query:
            episode_queryset = episode_queryset.filter(
                Q(title__icontains=episode_query) | Q(content__icontains=episode_query),
            )

        seasons = season_queryset.filter(media_title=self.object).prefetch_related(
            Prefetch('episodes', queryset=episode_queryset),
        )
        seasons = list(seasons)
        for season in seasons:
            season.visible_episode_count = len(season.episodes.all())
        show_movie_content = (
            self.object.kind == MediaTitle.Kind.MOVIE and (
                is_manager or self.object.movie_content_status == MediaTitle.ContentStatus.PUBLISHED
            )
        )
        visible_episode_count = sum(season.visible_episode_count for season in seasons)
        context.update(
            {
                'can_manage_library': is_manager,
                'seasons': seasons,
                'show_movie_content': show_movie_content,
                'season_count': len(seasons),
                'visible_episode_count': visible_episode_count,
                'episode_query': episode_query,
            }
        )
        return context


class SupportLibraryEpisodeDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'episode'
    model = Episode
    template_name = 'support_library/episode_detail.html'

    def get_object(self, queryset=None):
        queryset = Episode.objects.select_related('season', 'season__media_title')
        if not can_manage_support_library(self.request.user):
            queryset = queryset.filter(
                is_active=True,
                status=Episode.Status.PUBLISHED,
                season__is_active=True,
                season__media_title__is_active=True,
            )
        return get_object_or_404(
            queryset,
            season__media_title__slug=self.kwargs['slug'],
            season__number=self.kwargs['season_number'],
            number=self.kwargs['episode_number'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        episode_queryset = self.object.season.episodes.order_by('number')
        if not can_manage_support_library(self.request.user):
            episode_queryset = episode_queryset.filter(is_active=True, status=Episode.Status.PUBLISHED)

        context.update(
            {
                'can_manage_library': can_manage_support_library(self.request.user),
                'previous_episode': episode_queryset.filter(number__lt=self.object.number).order_by('-number').first(),
                'next_episode': episode_queryset.filter(number__gt=self.object.number).order_by('number').first(),
            }
        )
        return context


class SupportLibraryManageMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class ManageTitleListView(SupportLibraryManageMixin, ListView):
    context_object_name = 'titles'
    model = MediaTitle
    permission_required = 'support_library.view_mediatitle'
    template_name = 'support_library/manage/title_list.html'

    def get_queryset(self):
        queryset = annotate_support_library_titles(MediaTitle.objects.all(), True)

        query = self.request.GET.get('q', '').strip()
        kind = self.request.GET.get('kind', '').strip()
        state = self.request.GET.get('state', '').strip()
        sort = self.request.GET.get('sort', 'alpha').strip()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(summary__icontains=query))
        if kind in {MediaTitle.Kind.SERIES, MediaTitle.Kind.MOVIE}:
            queryset = queryset.filter(kind=kind)
        if state == 'active':
            queryset = queryset.filter(is_active=True)
        elif state == 'inactive':
            queryset = queryset.filter(is_active=False)
        return apply_support_library_sort(queryset, sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'current_query': self.request.GET.get('q', '').strip(),
                'current_kind': self.request.GET.get('kind', '').strip(),
                'current_state': self.request.GET.get('state', '').strip(),
                'current_sort': self.request.GET.get('sort', 'alpha').strip(),
                'results_count': context['titles'].count(),
            }
        )
        return context


class ManageTitleCreateView(SupportLibraryManageMixin, CreateView):
    form_class = MediaTitleForm
    permission_required = 'support_library.add_mediatitle'
    template_name = 'support_library/manage/title_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Support Library title created successfully.')
        return response

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.object.slug})


class ManageTitleUpdateView(SupportLibraryManageMixin, UpdateView):
    form_class = MediaTitleForm
    model = MediaTitle
    permission_required = 'support_library.change_mediatitle'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    template_name = 'support_library/manage/title_form.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Support Library title updated successfully.')
        return response

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.object.slug})


class ManageTitleDeleteView(SupportLibraryManageMixin, DeleteView):
    model = MediaTitle
    permission_required = 'support_library.delete_mediatitle'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('support_library:manage-title-list')
    template_name = 'support_library/manage/confirm_delete.html'

    def form_valid(self, form):
        messages.success(self.request, 'Support Library title deleted successfully.')
        return super().form_valid(form)


class ManageSeasonCreateView(SupportLibraryManageMixin, CreateView):
    form_class = SeasonForm
    permission_required = 'support_library.add_season'
    template_name = 'support_library/manage/season_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.media_title = get_object_or_404(MediaTitle, slug=self.kwargs['slug'])
        if self.media_title.kind != MediaTitle.Kind.SERIES:
            raise Http404('Seasons are only available for series.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.media_title = self.media_title
        response = super().form_valid(form)
        messages.success(self.request, 'Season created successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_title'] = self.media_title
        return context

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.media_title.slug})


class ManageSeasonUpdateView(SupportLibraryManageMixin, UpdateView):
    form_class = SeasonForm
    model = Season
    permission_required = 'support_library.change_season'
    template_name = 'support_library/manage/season_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Season updated successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['media_title'] = self.object.media_title
        return context

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.object.media_title.slug})


class ManageSeasonDeleteView(SupportLibraryManageMixin, DeleteView):
    model = Season
    permission_required = 'support_library.delete_season'
    template_name = 'support_library/manage/confirm_delete.html'

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.object.media_title.slug})

    def form_valid(self, form):
        messages.success(self.request, 'Season deleted successfully.')
        return super().form_valid(form)


class ManageEpisodeCreateView(SupportLibraryManageMixin, CreateView):
    form_class = EpisodeForm
    permission_required = 'support_library.add_episode'
    template_name = 'support_library/manage/episode_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.season = get_object_or_404(Season.objects.select_related('media_title'), pk=self.kwargs['season_pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.season = self.season
        form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Episode created successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['season'] = self.season
        context['media_title'] = self.season.media_title
        return context

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.season.media_title.slug})


class ManageEpisodeUpdateView(SupportLibraryManageMixin, UpdateView):
    form_class = EpisodeForm
    model = Episode
    permission_required = 'support_library.change_episode'
    template_name = 'support_library/manage/episode_form.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Episode updated successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['season'] = self.object.season
        context['media_title'] = self.object.season.media_title
        return context

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.object.season.media_title.slug})


class ManageEpisodeDeleteView(SupportLibraryManageMixin, DeleteView):
    model = Episode
    permission_required = 'support_library.delete_episode'
    template_name = 'support_library/manage/confirm_delete.html'

    def get_success_url(self):
        return reverse('support_library:title-detail', kwargs={'slug': self.object.season.media_title.slug})

    def form_valid(self, form):
        messages.success(self.request, 'Episode deleted successfully.')
        return super().form_valid(form)
