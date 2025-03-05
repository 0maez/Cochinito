from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm
from .models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment


def home(request):
    return render(request, "finance/home.html")

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("income_form")
    else:
        form = RegisterForm()
    return render(request, "finance/register.html", {"form": form})

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
    
    # Renderiza el dashboard con los datos
    return render(request, "finance/dashboard.html", {
        "income_sources": income_sources,
        "basic_expenses": basic_expenses,
        "wish_expenses": wish_expenses,
        "savings_investments": savings_investments,
    })

