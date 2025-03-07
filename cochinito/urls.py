"""
URL configuration for cochinito project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from finance import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('finance.urls')),  # Esto hará que la raíz se dirija a las URLs definidas en finance/urls.py
    path("accounts/login/", auth_views.LoginView.as_view(), name='login'),
    path("accounts/logout/", auth_views.LoginView.as_view(), name='logout'),  # Cambié LoginView por LogoutView
    path("finance/register/", views.register, name="register"),
    path("finance/income-form/", views.income_form, name="income_form"),
    path("finance/basic-expense-form/", views.basic_expense_form, name="basic_expense_form"),
    path("finance/wish-expense-form/", views.wish_expense_form, name="wish_expense_form"),
    path("finance/savings-investment-form/", views.savings_investment_form, name="savings_investment_form"),
    path("finance/dashboard/", views.dashboard, name="dashboard"),  # Cambié profile a dashboard
    path("accounts/", include("django.contrib.auth.urls")),  # Esto incluye las URLs predeterminadas de autenticación
]




