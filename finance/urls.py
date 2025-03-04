from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Página de inicio
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
]