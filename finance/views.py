from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm, BudgetForm
from .models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Budget
from decimal import Decimal



def home(request):
    return render(request, "finance/home.html")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Esto crea al usuario y guarda el perfil
            login(request, user)  # Loguea al usuario automáticamente
            return redirect('create_budget')  # Redirige a la página de inicio o alguna otra página
    else:
        form = RegisterForm()  # Usamos el formulario personalizado
    return render(request, 'finance/register.html', {'form': form})


def income_form(request):
    if request.method == "POST":
        form = IncomeForm(request.POST)
        if form.is_valid():
            income_source_ids = list(form.cleaned_data["income_sources"].values_list("id", flat=True))
            request.session["income_sources_ids"] = income_source_ids
            return redirect("basic_expense_form")
    else:
        form = IncomeForm()
    return render(request, "finance/income_form.html", {"form": form})

def basic_expense_form(request):
    income_source_ids = request.session.get("income_source_ids", [])
    income_sources = IncomeSource.objects.filter(id__in=income_source_ids)
    if request.method == "POST":
        form = BasicExpenseForm(request.POST)
        if form.is_valid():
            basic_expense_ids = list(form.cleaned_data["basic_expenses"].values_list("id", flat=True))
            request.session["basic_expense_ids"] = basic_expense_ids
            return redirect("wish_expense_form")
    else:
        form = BasicExpenseForm()
    return render(request, "finance/basic_expense_form.html", {"form": form, "income_sources": income_sources})


def wish_expense_form(request):
    basic_expense_ids = request.session.get("basic_expense_ids", [])
    basic_expenses = BasicExpense.objects.filter(id__in=basic_expense_ids)
    if request.method == "POST":
        form = WishExpenseForm(request.POST)
        if form.is_valid():
            wish_expense_ids = list(form.cleaned_data["wish_expenses"].values_list("id", flat=True))
            request.session["wish_expense_ids"] = wish_expense_ids
            return redirect("savings_investment_form")
    else:
        form = WishExpenseForm()
    return render(request, "finance/wish_expense_form.html", {"form": form})

def savings_investment_form(request):
    
    wish_expense_ids = request.session.get("wish_expense_ids", [])
    wish_expenses = WishExpense.objects.filter(id__in=wish_expense_ids)
    
    if request.method == "POST":
        form = SavingsInvestmentForm(request.POST)
        if form.is_valid():
            # Guarda los IDs de las opciones de ahorro e inversión seleccionadas
            savings_investment_ids = list(form.cleaned_data["savings_investments"].values_list("id", flat=True))
            request.session["savings_investment_ids"] = savings_investment_ids
            return redirect("dashboard")  # Redirige al dashboard después de completar todos los formularios
    else:
        form = SavingsInvestmentForm()
    return render(request, "finance/savings_investment_form.html", {"form": form})  

@login_required
def dashboard(request):
    # Recupera todos los IDs almacenados en la sesión
    income_source_ids = request.session.get("income_source_ids", [])
    basic_expense_ids = request.session.get("basic_expense_ids", [])
    wish_expense_ids = request.session.get("wish_expense_ids", [])
    savings_investment_ids = request.session.get("savings_investment_ids", [])

    # Obtén los objetos completos desde la base de datos
    income_sources = IncomeSource.objects.filter(id__in=income_source_ids)
    basic_expenses = BasicExpense.objects.filter(id__in=basic_expense_ids)
    wish_expenses = WishExpense.objects.filter(id__in=wish_expense_ids)
    savings_investments = SavingsInvestment.objects.filter(id__in=savings_investment_ids)
    
    # Obtener el presupuesto del usuario actual (si existe)
    user_budget = Budget.objects.filter(user=request.user).first()  # Suponiendo que usas el modelo Budget para almacenar el presupuesto

    # Verificamos si el presupuesto existe, y si es así, calculamos los valores de los porcentajes
    available_for_basic_expenses = Decimal(0)
    available_for_wish_expenses = Decimal(0)
    available_for_savings = Decimal(0)
    total_amount = Decimal(0)
    if user_budget:
        total_amount = user_budget.total_amount  # Usamos el total_amount directamente para los cálculos de los porcentajes
        available_for_basic_expenses = total_amount * Decimal(0.50)
        available_for_wish_expenses = total_amount * Decimal(0.30)
        available_for_savings = total_amount * Decimal(0.20)

    # Renderiza el dashboard con los datos
    return render(request, "finance/dashboard.html", {
        "income_sources": income_sources,
        "basic_expenses": basic_expenses,
        "wish_expenses": wish_expenses,
        "savings_investments": savings_investments,
        "user_budget": user_budget,
        "total_amount": total_amount,
        "available_for_basic_expenses": available_for_basic_expenses,
        "available_for_wish_expenses": available_for_wish_expenses,
        "available_for_savings": available_for_savings,
    })

@login_required
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.current_balance = budget.total_amount  # Asignar saldo inicial igual al presupuesto inicial
            budget.save()
            return redirect('basic_expense_form')  # Redirige al siguiente paso
    else:
        form = BudgetForm()
    return render(request, 'finance/create_budget.html', {'form': form})