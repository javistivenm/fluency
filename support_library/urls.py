from django.urls import path

from .views import (
    ManageEpisodeCreateView,
    ManageEpisodeDeleteView,
    ManageEpisodeUpdateView,
    ManageSeasonCreateView,
    ManageSeasonDeleteView,
    ManageSeasonUpdateView,
    ManageTitleCreateView,
    ManageTitleDeleteView,
    ManageTitleListView,
    ManageTitleUpdateView,
    SupportLibraryCatalogView,
    SupportLibraryEpisodeDetailView,
    SupportLibraryTitleDetailView,
)

app_name = 'support_library'

urlpatterns = [
    path('', SupportLibraryCatalogView.as_view(), name='catalog'),
    path('manage/', ManageTitleListView.as_view(), name='manage-title-list'),
    path('manage/titles/create/', ManageTitleCreateView.as_view(), name='manage-title-create'),
    path('manage/titles/<slug:slug>/edit/', ManageTitleUpdateView.as_view(), name='manage-title-update'),
    path('manage/titles/<slug:slug>/delete/', ManageTitleDeleteView.as_view(), name='manage-title-delete'),
    path('manage/titles/<slug:slug>/seasons/create/', ManageSeasonCreateView.as_view(), name='manage-season-create'),
    path('manage/seasons/<int:pk>/edit/', ManageSeasonUpdateView.as_view(), name='manage-season-update'),
    path('manage/seasons/<int:pk>/delete/', ManageSeasonDeleteView.as_view(), name='manage-season-delete'),
    path('manage/seasons/<int:season_pk>/episodes/create/', ManageEpisodeCreateView.as_view(), name='manage-episode-create'),
    path('manage/episodes/<int:pk>/edit/', ManageEpisodeUpdateView.as_view(), name='manage-episode-update'),
    path('manage/episodes/<int:pk>/delete/', ManageEpisodeDeleteView.as_view(), name='manage-episode-delete'),
    path(
        '<slug:slug>/season/<int:season_number>/episode/<int:episode_number>/',
        SupportLibraryEpisodeDetailView.as_view(),
        name='episode-detail',
    ),
    path('<slug:slug>/', SupportLibraryTitleDetailView.as_view(), name='title-detail'),
]
