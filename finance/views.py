from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm, BudgetForm, TransactionForm, ReminderForm, UserForm, ProfileForm
from .models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Budget, Transaction, Reminder, Profile
from decimal import Decimal

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
            selected_income_sources = form.cleaned_data["income_sources"]
            for source in selected_income_sources:
                IncomeSource.objects.get_or_create(user=request.user, name=source.name)
            return redirect("basic_expense_form")
    else:
        form = IncomeForm()
    return render(request, "finance/income_form.html", {"form": form})


def basic_expense_form(request):
    if request.method == "POST":
        form = BasicExpenseForm(request.POST) 
        if form.is_valid():
            selected_basic_expenses = form.cleaned_data["basic_expenses"]
            for expense in selected_basic_expenses:
                BasicExpense.objects.get_or_create(user=request.user, name=expense.name)
            return redirect("wish_expense_form")
    else:
        form = BasicExpenseForm()  
    return render(request, "finance/basic_expense_form.html", {"form": form})

def wish_expense_form(request):
    if request.method == "POST":
        form = WishExpenseForm(request.POST) 
        if form.is_valid():
            selected_wish_expenses = form.cleaned_data["wish_expenses"]
            for wish in selected_wish_expenses:
                WishExpense.objects.get_or_create(user=request.user, name=wish.name)
            return redirect("savings_investment_form")
    else:
        form = WishExpenseForm()  
    return render(request, "finance/wish_expense_form.html", {"form": form})


def savings_investment_form(request):
    if request.method == "POST":
        form = SavingsInvestmentForm(request.POST)
        if form.is_valid():
            selected_savings = form.cleaned_data["savings_investments"]
            for investment in selected_savings:
                SavingsInvestment.objects.get_or_create(user=request.user, name=investment.name)
            return redirect("dashboard")
    else:
        form = SavingsInvestmentForm() 
    return render(request, "finance/savings_investment_form.html", {"form": form})

@login_required
def dashboard(request):
    user_budget = Budget.objects.filter(user=request.user).first()
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    income_sources = IncomeSource.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user, is_paid=False)

    basic_expenses = Transaction.objects.filter(user=request.user, basic_expense__isnull=False)
    wish_expenses = Transaction.objects.filter(user=request.user, wish_expense__isnull=False)
    savings_investments = Transaction.objects.filter(user=request.user, savings_investment__isnull=False)

    # Definir valores predeterminados en caso de que no haya presupuesto
    available_for_basic_expenses = Decimal(0)
    available_for_wish_expenses = Decimal(0)
    available_for_savings_expenses = Decimal(0)
    spent_on_basic = Decimal(0)
    spent_on_wish = Decimal(0)
    spent_on_savings = Decimal(0)
    total_amount = Decimal(0)

    if user_budget:
        total_amount = user_budget.total_amount
        spent_on_basic = sum(expense.amount for expense in basic_expenses)
        spent_on_wish = sum(expense.amount for expense in wish_expenses)
        spent_on_savings = sum(expense.amount for expense in savings_investments)

        available_for_basic_expenses = user_budget.basic_expenses - spent_on_basic
        available_for_wish_expenses = user_budget.wish_expenses - spent_on_wish
        available_for_savings_expenses = user_budget.savings_investments - spent_on_savings

    percentage_basic = (spent_on_basic / user_budget.basic_expenses) * 100 if user_budget and user_budget.basic_expenses > 0 else 0
    percentage_wish = (spent_on_wish / user_budget.wish_expenses) * 100 if user_budget and user_budget.wish_expenses > 0 else 0
    percentage_savings = (spent_on_savings / user_budget.savings_investments) * 100 if user_budget and user_budget.savings_investments > 0 else 0

    is_balance_low = user_budget.current_balance <= (user_budget.total_amount * Decimal('0.20')) if user_budget else False
    exceeded_basic = available_for_basic_expenses < 0
    exceeded_wish = available_for_wish_expenses < 0

    context = {
        "user_budget": user_budget,
        "transactions": transactions,
        "total_amount": total_amount,
        "available_for_basic_expenses": available_for_basic_expenses,
        "available_for_wish_expenses": available_for_wish_expenses,
        "available_for_savings_expenses": available_for_savings_expenses,
        "income_sources": income_sources,
        "basic_expenses": basic_expenses,
        "wish_expenses": wish_expenses,
        "savings_investments": savings_investments,
        "reminders": reminders,
        "percentage_basic": percentage_basic,
        "percentage_wish": percentage_wish,
        "percentage_savings": percentage_savings,
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
    
class SavingsCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/add_savings.html'
    success_url = reverse_lazy('transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  
        kwargs['transaction_type'] = 'savings'  
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user  
        form.instance.transaction_type = 'savings'  
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

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "finance/profile.html"

    def get(self, request, *args, **kwargs):
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        income_form = IncomeForm()
        expense_form = BasicExpenseForm()
        wish_expense_form = WishExpenseForm()
        savings_form = SavingsInvestmentForm()
        
        budget = Budget.objects.get(user=request.user)
        transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')[:2]
        incomes = IncomeSource.objects.filter(user=request.user)
        basic_expenses = BasicExpense.objects.filter(user=request.user)
        wish_expenses = WishExpense.objects.filter(user=request.user)
        savings = SavingsInvestment.objects.filter(user=request.user)

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'income_form': income_form,
            'expense_form': expense_form,
            'wish_expense_form': wish_expense_form,
            'savings_form': savings_form,
            'budget': budget,
            'transactions': transactions,
            'incomes': incomes,
            'basic_expenses': basic_expenses,
            'wish_expenses': wish_expenses,
            'savings': savings,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        income_form = IncomeSourceForm(request.POST)
        expense_form = BasicExpenseForm(request.POST)
        wish_expense_form = WishExpenseForm(request.POST)
        savings_form = SavingsInvestmentForm(request.POST)

        # Verificar qué formulario se ha enviado
        if 'profile_form_submit' in request.POST and user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')

        if 'income_form_submit' in request.POST and income_form.is_valid():
            income_form.save()
            return redirect('profile')

        if 'expense_form_submit' in request.POST and expense_form.is_valid():
            expense_form.save()
            return redirect('profile')

        if 'wish_expense_form_submit' in request.POST and wish_expense_form.is_valid():
            wish_expense_form.save()
            return redirect('profile')

        if 'savings_form_submit' in request.POST and savings_form.is_valid():
            savings_form.save()
            return redirect('profile')

        # Si no se guarda nada, renderiza la vista con los formularios
        return self.get(request)


# Eliminar ingreso
def delete_income(request, income_id):
    income = get_object_or_404(IncomeSource, id=income_id, user=request.user)
    income.delete()
    return redirect('profile')

# Eliminar gasto básico
def delete_expense(request, expense_id):
    expense = get_object_or_404(BasicExpense, id=expense_id, user=request.user)
    expense.delete()
    return redirect('profile')

# Eliminar gasto de deseo
def delete_wish_expense(request, wish_expense_id):
    wish_expense = get_object_or_404(WishExpense, id=wish_expense_id, user=request.user)
    wish_expense.delete()
    return redirect('profile')

# Eliminar ahorro
def delete_saving(request, saving_id):
    saving = get_object_or_404(SavingsInvestment, id=saving_id, user=request.user)
    saving.delete()
    return redirect('profile')