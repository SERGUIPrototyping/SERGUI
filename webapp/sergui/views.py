# Create your views here.
from django.views.generic import FormView
from . import search_form
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os


def sergui(request):
    return render(request, 'sergui.html')