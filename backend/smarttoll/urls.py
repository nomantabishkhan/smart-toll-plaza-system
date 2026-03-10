from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from smarttoll.toll import views as toll_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("smarttoll.toll.api")),
    path("accounts/login/", LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("", toll_views.dashboard, name="dashboard"),
]
