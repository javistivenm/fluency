from django.contrib import admin

from .models import Episode, MediaTitle, Season


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0


@admin.register(MediaTitle)
class MediaTitleAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'is_active', 'movie_content_status', 'published_at')
    list_filter = ('kind', 'is_active', 'movie_content_status')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'summary', 'movie_content')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('media_title', 'number', 'title', 'is_active')
    list_filter = ('is_active', 'media_title')
    inlines = (EpisodeInline,)


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('season', 'number', 'title', 'status', 'is_active', 'published_at')
    list_filter = ('status', 'is_active', 'season__media_title')
    search_fields = ('title', 'content')
