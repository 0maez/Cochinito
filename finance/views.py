from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm, BudgetForm, TransactionForm
from .models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Budget, Transaction
from decimal import Decimal
from finance.load_categories import load_categories

def home(request):
    return render(request, "finance/home.html")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            login(request, user)
            load_categories(user)  
            return redirect('create_budget')  
    else:
        form = RegisterForm()  
    return render(request, 'finance/register.html', {'form': form})

def income_form(request):
    if request.method == "POST":
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            selected_income_sources = form.cleaned_data["income_sources"]
            for source in selected_income_sources:
                IncomeSource.objects.get_or_create(user=request.user, name=source.name)
            IncomeSource.objects.filter(user=request.user).exclude(id__in=selected_income_sources.values_list("id", flat=True)).delete()
            income_source_ids = list(selected_income_sources.values_list("id", flat=True))
            request.session["income_sources_ids"] = income_source_ids
            return redirect("basic_expense_form")
    else:
        form = IncomeForm(user=request.user) 
    return render(request, "finance/income_form.html", {"form": form})

def basic_expense_form(request):
    if request.method == "POST":
        form = BasicExpenseForm(request.POST, user=request.user) 
        if form.is_valid():
            selected_basic_expenses = form.cleaned_data["basic_expenses"]
            for expense in selected_basic_expenses:
                BasicExpense.objects.get_or_create(user=request.user, name=expense.name)
            BasicExpense.objects.filter(user=request.user).exclude(id__in=selected_basic_expenses.values_list("id", flat=True)).delete()
            basic_expense_ids = list(selected_basic_expenses.values_list("id", flat=True))
            request.session["basic_expense_ids"] = basic_expense_ids
            return redirect("wish_expense_form")
    else:
        form = BasicExpenseForm(user=request.user)  
    return render(request, "finance/basic_expense_form.html", {"form": form})

def wish_expense_form(request):
    if request.method == "POST":
        form = WishExpenseForm(request.POST, user=request.user) 
        if form.is_valid():
            selected_wish_expenses = form.cleaned_data["wish_expenses"]
            for wish in selected_wish_expenses:
                WishExpense.objects.get_or_create(user=request.user, name=wish.name)
            WishExpense.objects.filter(user=request.user).exclude(id__in=selected_wish_expenses.values_list("id", flat=True)).delete()
            wish_expense_ids = list(selected_wish_expenses.values_list("id", flat=True))
            request.session["wish_expense_ids"] = wish_expense_ids
            return redirect("savings_investment_form")
    else:
        form = WishExpenseForm(user=request.user)  
    return render(request, "finance/wish_expense_form.html", {"form": form})

def savings_investment_form(request):
    if request.method == "POST":
        form = SavingsInvestmentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save(request.user)  
            selected_savings = form.cleaned_data["savings_investments"]
            SavingsInvestment.objects.filter(user=request.user).exclude(id__in=selected_savings.values_list("id", flat=True)).delete()
            return redirect("profile")
    else:
        form = SavingsInvestmentForm(user=request.user)
    return render(request, "finance/savings_investment_form.html", {"form": form})

@login_required
def profile(request):
    
    user_budget = Budget.objects.filter(user=request.user).first()
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    income_sources = IncomeSource.objects.filter(user=request.user)
    basic_expenses = BasicExpense.objects.filter(user=request.user)
    wish_expenses = WishExpense.objects.filter(user=request.user)
    savings_investments = SavingsInvestment.objects.filter(user=request.user)
    available_for_basic_expenses = Decimal(0)
    available_for_wish_expenses = Decimal(0)
    available_for_savings = Decimal(0)
    total_amount = Decimal(0)

    if user_budget:
        total_amount = user_budget.total_amount
        available_for_basic_expenses = total_amount * Decimal('0.50')
        available_for_wish_expenses = total_amount * Decimal('0.30')
        available_for_savings = total_amount * Decimal('0.20')

    return render(request, "finance/profile.html", {
        "user_budget": user_budget,
        "transactions": transactions,
        "total_amount": total_amount,
        "available_for_basic_expenses": available_for_basic_expenses,
        "available_for_wish_expenses": available_for_wish_expenses,
        "available_for_savings": available_for_savings,
        "income_sources": income_sources,  
        "basic_expenses": basic_expenses, 
        "wish_expenses": wish_expenses,  
        "savings_investments": savings_investments,  
    })

@login_required
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.current_balance = budget.total_amount  
            budget.save()
            return redirect('income_form')  
    else:
        form = BudgetForm()
    return render(request, 'finance/create_budget.html', {'form': form})

class IncomeCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/add_income.html'
    success_url = reverse_lazy('transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        kwargs['transaction_type'] = 'income' 
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  
        form.instance.transaction_type = 'income' 
        budget = Budget.objects.filter(user=self.request.user).first()  
        if budget:
            form.instance.budget = budget  
        return super().form_valid(form)
    
class ExpenseCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/add_expense.html'
    success_url = reverse_lazy('transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        kwargs['transaction_type'] = 'expense'  
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  
        form.instance.transaction_type = 'expense'  
        budget = Budget.objects.filter(user=self.request.user).first()  
        if budget:
            form.instance.budget = budget  
        return super().form_valid(form)

class TransactionListView(ListView):
    model = Transaction
    template_name = 'finance/transactions/transaction_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transactions/transaction_form.html'
    context_object_name = 'transactions'
    success_url = reverse_lazy('transaction_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        return kwargs

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'finance/transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)