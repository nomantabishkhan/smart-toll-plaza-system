from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest


@login_required
def dashboard(request: HttpRequest):
    return render(request, "toll/dashboard.html")
