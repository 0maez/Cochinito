from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Página de inicio
    path("register/", views.register, name="register"),
    path('create-budget/', views.create_budget, name='create_budget'),
    path('basic-expense/', views.basic_expense_form, name='basic_expense_form'),  # La vista para el siguiente paso
]