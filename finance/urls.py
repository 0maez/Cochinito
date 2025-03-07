from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Página de inicio
    path("register/", views.register, name="register"),
    path('create-budget/', views.create_budget, name='create_budget'),
    path('basic-expense/', views.basic_expense_form, name='basic_expense_form'),  # La vista para el siguiente paso
    path('reminders/create/', views.create_reminder, name='create_reminder'),
    path('mark_reminder_paid/', views.mark_reminder_paid, name='mark_reminder_paid'),
    path('reminders/', views.reminder_list, name='reminder_list'),

]