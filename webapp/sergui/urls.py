# search/urls.py
from django.urls import path

from .views import sergui

urlpatterns = [
    path('sergui/', sergui, name='sergui')
]