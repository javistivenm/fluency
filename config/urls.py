from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('daily-tasks/', include('daily_tasks.urls')),
    path('summernote/', include('django_summernote.urls')),
    path('writing/', include('fluency.urls')),
    path('support-library/', include('support_library.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
