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
from finance.views import IncomeCreateView, ExpenseCreateView, SavingsCreateView, TransactionUpdateView, TransactionDeleteView, TransactionListView, summary


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('finance.urls')),
    path("accounts/login/", auth_views.LoginView.as_view(), name='login'),
    # Asegúrate de usar LogoutView para el cierre de sesión
    path("accounts/logout/", auth_views.LogoutView.as_view(), name='logout'),  
    path("finance/register/", views.register, name="register"),
    path("finance/income-form/", views.income_form, name="income_form"),
    path("finance/basic-expense-form/", views.basic_expense_form, name="basic_expense_form"),
    path("finance/wish-expense-form/", views.wish_expense_form, name="wish_expense_form"),
    path("finance/savings-investment-form/", views.savings_investment_form, name="savings_investment_form"),
    path("finance/dashboard/", views.dashboard, name="dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('transaction/add/income/', IncomeCreateView.as_view(), name='add_income'),
    path('transaction/add/expense/', ExpenseCreateView.as_view(), name='add_expense'),
    path('transaction/add/savings/', SavingsCreateView.as_view(), name='add_savings'),
    path('transactions/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view(), name='update_transaction'),
    path('transactions/delete/<int:pk>/', TransactionDeleteView.as_view(), name='delete_transaction'),
    path('finance/budget-list/', views.budget_list, name='budget_list'),  # URL para budget_list
    path('finance/edit-budget/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('finance/set-active-budget/<int:budget_id>/', views.set_active_budget, name='set_active_budget'),
    path('finance/summary/', views.summary, name='summary'),
    path("recursos_educativos/", views.module_list, name="module_list"),
    path("modulo/<int:modulo_id>/", views.module_detail, name="module_detail"),
    path("completar-modulo/<int:modulo_id>/", views.complete_module, name="completar_modulo"),
]