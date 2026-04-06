from django.urls import path

from . import views

app_name = 'fluency'

urlpatterns = [
    path('', views.home, name='home'),
    path('level/', views.set_level, name='set-level'),
    path('daily/', views.daily_challenge, name='daily-challenge'),
]
