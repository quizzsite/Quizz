from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

def Exception404(request, exception):
    return render(request, "quizzes/404.html")

def index(request):
    return render(request, 'quizzes/index.html')