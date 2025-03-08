from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), 
    path("register/", views.register, name="register"),
    path('create-budget/', views.create_budget, name='create_budget'),
    path('basic-expense/', views.basic_expense_form, name='basic_expense_form'),  
]