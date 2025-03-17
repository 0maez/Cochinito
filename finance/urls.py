from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  
    path("", views.home, name="home"), 
    path("register/", views.register, name="register"),
    path('create-budget/', views.create_budget, name='create_budget'),
    path('basic-expense/', views.basic_expense_form, name='basic_expense_form'), 
    path('reminders/create/', views.create_reminder, name='create_reminder'),
    path('mark_reminder_paid/', views.mark_reminder_paid, name='mark_reminder_paid'),
    path('reminders/', views.reminder_list, name='reminder_list'),
    path('basic-expense/', views.basic_expense_form, name='basic_expense_form'),  
    path('about-us/', views.about_us, name='about_us'),
    path('features/', views.features, name='features'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]