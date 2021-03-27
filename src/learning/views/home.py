""" Lean home view """
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def home_view(request: HttpRequest):
    return render(request, 'learning/home.html')
