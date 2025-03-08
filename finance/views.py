from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm, BudgetForm, ReminderForm
from .models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Budget, Reminder
from decimal import Decimal
from datetime import date, timedelta


def home(request):
    return render(request, "finance/home.html")


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user)  
            return redirect('create_budget')  
    else:
        form = RegisterForm()  
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
            savings_investment_ids = list(form.cleaned_data["savings_investments"].values_list("id", flat=True))
            request.session["savings_investment_ids"] = savings_investment_ids
            return redirect("dashboard")  
    else:
        form = SavingsInvestmentForm()
    return render(request, "finance/savings_investment_form.html", {"form": form})


@login_required
def dashboard(request):

    user_budget = Budget.objects.filter(user=request.user).first()
    if not user_budget:
        return redirect('create_budget')

    income_source_ids = request.session.get("income_source_ids", [])
    basic_expense_ids = request.session.get("basic_expense_ids", [])
    wish_expense_ids = request.session.get("wish_expense_ids", [])
    savings_investment_ids = request.session.get("savings_investment_ids", [])

    income_sources = IncomeSource.objects.filter(user=request.user)
    basic_expenses = BasicExpense.objects.filter(id__in=basic_expense_ids)
    wish_expenses = WishExpense.objects.filter(id__in=wish_expense_ids)
    savings_investments = SavingsInvestment.objects.filter(id__in=savings_investment_ids)

    total_amount = user_budget.total_amount
    available_for_basic_expenses = total_amount * Decimal('0.50')
    available_for_wish_expenses = total_amount * Decimal('0.30')
    available_for_savings = total_amount * Decimal('0.20')

    reminders = Reminder.objects.filter(user=request.user, is_paid=False).order_by('date')

    context = {
        'user_budget': user_budget,
        'income_sources': income_sources,
        'basic_expenses': basic_expenses,
        'wish_expenses': wish_expenses,
        'savings_investments': savings_investments,
        'total_amount': total_amount,
        'available_for_basic_expenses': available_for_basic_expenses,
        'available_for_wish_expenses': available_for_wish_expenses,
        'available_for_savings': available_for_savings,
        'reminders': reminders,
    }

    return render(request, 'finance/dashboard.html', context)


@login_required
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.current_balance = budget.total_amount  
            budget.save()
            return redirect('basic_expense_form')  
    else:
        form = BudgetForm()
    return render(request, 'finance/create_budget.html', {'form': form})


@login_required
def create_reminder(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            return redirect('dashboard')  
    else:
        form = ReminderForm()
    return render(request, 'finance/create_reminder.html', {'form': form})


from django.shortcuts import render, redirect
from .models import Reminder

@login_required
def mark_reminder_paid(request):
    if request.method == 'POST':
        reminder_ids = request.POST.getlist('reminder_ids')
        for reminder_id in reminder_ids:
            try:
                reminder = Reminder.objects.get(id=reminder_id, user=request.user)
                reminder.is_paid = True
                reminder.save()
            except Reminder.DoesNotExist:
                pass
    return redirect('reminder_list')  


@login_required
def reminder_list(request):

    reminders = Reminder.objects.filter(user=request.user, is_paid=False).order_by('date')
    context = {
        'reminders': reminders,
    }
    return render(request, 'finance/reminder_list.html', context)
