from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.wheel_view, name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.TeamLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("wheel/", views.wheel_view, name="wheel"),
    path("spin/", views.spin_view, name="spin"),
]
