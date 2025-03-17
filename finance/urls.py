from django.urls import path
from . import views
from .views import ProfileUpdateView  # Asegúrate de importar la vista correctamente

urlpatterns = [
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
    path('profile/', ProfileUpdateView.as_view(), name='profile'),  # Aquí está la ruta de la vista ProfileUpdateView
    path('delete-income/<int:income_id>/', views.delete_income, name='delete_income'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('delete-wish-expense/<int:wish_expense_id>/', views.delete_wish_expense, name='delete_wish_expense'),
    path('delete-saving/<int:saving_id>/', views.delete_saving, name='delete_saving'),
]
