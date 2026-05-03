from django.urls import path
from . import views

urlpatterns = [
    path("csrf/", views.csrf_token, name="csrf_token"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("status/", views.auth_status, name="auth_status"),
    path("access/", views.access_info, name="access_info"),
    path("google/login/", views.google_login, name="google_login"),
    path("google/callback/", views.google_callback, name="google_callback"),
]
