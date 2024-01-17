# search/urls.py
from django.urls import path

from .views import rasa

urlpatterns = [
    path('rasa/', rasa, name='rasa'),
]