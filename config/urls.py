from django.contrib import admin
from django.urls import path
from config.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]
