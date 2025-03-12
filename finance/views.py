from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm, BudgetForm, TransactionForm, ReminderForm
from decimal import Decimal
from finance.models import Budget, Transaction, Reminder
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
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            selected_sources = form.cleaned_data["income_sources"]
            request.user.income_sources.add(*selected_sources)
            return redirect("basic_expense_form")
    else:
        form = IncomeForm(user=request.user)
    return render(request, "finance/income_form.html", {"form": form})

def basic_expense_form(request):
    if request.method == "POST":
        form = BasicExpenseForm(request.POST, user=request.user) 
        if form.is_valid():
            selected_sources = form.cleaned_data["basic_expenses"]
            request.user.basic_expenses.add(*selected_sources)
            return redirect("wish_expense_form")
    else:
        form = BasicExpenseForm(user=request.user)  
    return render(request, "finance/basic_expense_form.html", {"form": form})

def wish_expense_form(request):
    if request.method == "POST":
        form = WishExpenseForm(request.POST, user=request.user)  
        if form.is_valid():
            selected_sources = form.cleaned_data["wish_expenses"]
            request.user.wish_expenses.add(*selected_sources)
            return redirect("savings_investment_form")
    else:
        form = WishExpenseForm(user=request.user)  
    return render(request, "finance/wish_expense_form.html", {"form": form})

def savings_investment_form(request):
    if request.method == "POST":
        form = SavingsInvestmentForm(request.POST, user=request.user)
        if form.is_valid():
            selected_sources = form.cleaned_data["savings_investments"]
            request.user.savings_investments.add(*selected_sources)
            return redirect("dashboard")
    else:
        form = SavingsInvestmentForm(user=request.user)  
    return render(request, "finance/savings_investment_form.html", {"form": form})

@login_required
def dashboard(request):
    user_budget = Budget.objects.filter(user=request.user).first()
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    income_sources = request.user.income_sources.all()
    basic_expenses = request.user.basic_expenses.all()
    wish_expenses = request.user.wish_expenses.all()
    savings_investments = request.user.savings_investments.all()  
    reminders = Reminder.objects.filter(user=request.user, is_paid=False)

    basic_expenses = Transaction.objects.filter(user=request.user, basic_expense__isnull=False)
    wish_expenses = Transaction.objects.filter(user=request.user, wish_expense__isnull=False)
    savings_investments = Transaction.objects.filter(user=request.user, savings_investment__isnull=False)

    available_for_basic_expenses = Decimal(0)
    available_for_wish_expenses = Decimal(0)
    available_for_savings = Decimal(0)
    spent_on_basic = Decimal(0)
    spent_on_wish = Decimal(0)
    total_amount = Decimal(0)

    if user_budget:
        total_amount = user_budget.total_amount
        available_for_basic_expenses = user_budget.basic_expenses - sum(expense.amount for expense in basic_expenses)
        available_for_wish_expenses = user_budget.wish_expenses - sum(expense.amount for expense in wish_expenses)
        available_for_savings = user_budget.savings_investments

        spent_on_basic = sum(expense.amount for expense in basic_expenses)
        spent_on_wish = sum(expense.amount for expense in wish_expenses)

    percentage_basic = (spent_on_basic / user_budget.basic_expenses) * 100 if user_budget.basic_expenses > 0 else 0
    percentage_wish = (spent_on_wish / user_budget.wish_expenses) * 100 if user_budget.wish_expenses > 0 else 0


    is_balance_low = user_budget.current_balance <= (user_budget.total_amount * Decimal('0.20'))

    exceeded_basic = available_for_basic_expenses < 0
    exceeded_wish = available_for_wish_expenses < 0

    context = {
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
        "reminders": reminders,
        "percentage_basic": percentage_basic,
        "percentage_wish": percentage_wish,
        "is_balance_low": is_balance_low,
        "exceeded_basic": exceeded_basic,
        "exceeded_wish": exceeded_wish,
    }
    return render(request, "finance/dashboard.html", context)

@login_required
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.current_balance = budget.total_amount  
            budget.current_balance = budget.total_amount  
            budget.save()
            return redirect('income_form')  
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
    
def about_us(request):
    return render(request, 'finance/about_us.html')

def features(request):
    return render(request, 'finance/features.html')
