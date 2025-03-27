from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from .forms import RegisterForm, IncomeForm, BasicExpenseForm, WishExpenseForm, SavingsInvestmentForm, BudgetForm, TransactionForm, ReminderForm, SummaryFilterForm
from .models import IncomeSource, BasicExpense, WishExpense, SavingsInvestment, Budget, Transaction, Reminder, Module, UserProgress
from decimal import Decimal
import csv
from datetime import timedelta
from io import BytesIO
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger




def home(request):
    return render(request, "finance/home.html")

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['from_registration'] = True
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
    user_budget = Budget.objects.filter(user=request.user, is_active=True).first() 
    transactions = Transaction.objects.filter(user=request.user, budget=user_budget).order_by('-created_at')
    income_sources = IncomeSource.objects.filter(user=request.user)
    reminders = Reminder.objects.filter(user=request.user, is_paid=False)

    basic_expenses = transactions.filter(basic_expense__isnull=False)
    wish_expenses = transactions.filter(wish_expense__isnull=False)
    savings_investments = transactions.filter(savings_investment__isnull=False)

    # Definir valores predeterminados en caso de que no haya presupuesto
    available_for_basic_expenses = Decimal(0)
    available_for_wish_expenses = Decimal(0)
    available_for_savings_investments = Decimal(0)
    spent_on_basic = Decimal(0)
    spent_on_wish = Decimal(0)
    spent_on_savings = Decimal(0)
    total_amount = Decimal(0)

    total_amount = user_budget.total_amount
    available_for_basic_expenses = user_budget.basic_expenses - sum(expense.amount for expense in basic_expenses)
    available_for_wish_expenses = user_budget.wish_expenses - sum(expense.amount for expense in wish_expenses)
    available_for_savings_investments = user_budget.available_savings - sum(expense.amount for expense in savings_investments)

    spent_on_basic = sum(expense.amount for expense in basic_expenses)
    spent_on_wish = sum(expense.amount for expense in wish_expenses)
    spent_on_savings = sum(expense.amount for expense in savings_investments)

    available_for_basic_expenses = user_budget.basic_expenses - spent_on_basic
    available_for_wish_expenses = user_budget.wish_expenses - spent_on_wish
    available_for_savings_investments = user_budget.savings_investments - spent_on_savings

    percentage_basic = (spent_on_basic / user_budget.basic_expenses) * 100 if user_budget and user_budget.basic_expenses > 0 else 0
    percentage_wish = (spent_on_wish / user_budget.wish_expenses) * 100 if user_budget and user_budget.wish_expenses > 0 else 0
    percentage_savings = (spent_on_savings / user_budget.savings_investments) * 100 if user_budget and user_budget.savings_investments > 0 else 0

    is_balance_low = user_budget.current_balance <= (user_budget.total_amount * Decimal('0.20')) if user_budget else False
    exceeded_basic = available_for_basic_expenses < 0
    exceeded_wish = available_for_wish_expenses < 0
    exceeded_savings = available_for_savings_investments < 0
    

    context = {
        "user_budget": user_budget,
        "transactions": transactions,
        "total_amount": total_amount,
        "available_for_basic_expenses": available_for_basic_expenses,
        "available_for_wish_expenses": available_for_wish_expenses,
        "available_for_savings_investments": available_for_savings_investments,
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
        "exceeded_savings": exceeded_savings,
    }
    
    return render(request, "finance/dashboard.html", context)


@login_required
def create_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.current_balance = form.cleaned_data['total_amount']
            budget.save()
        
            if 'from_registration' in request.session:
                del request.session['from_registration']  
                return redirect('income_form')
            
            messages.success(request, "Nuevo presupuesto creado exitosamente")
            return redirect('dashboard')
    else:
        form = BudgetForm(user=request.user)
    
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
    paginate_by = 10  # Muestra 10 transacciones por página

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transactions = self.get_queryset()
        paginator = Paginator(transactions, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            transactions = paginator.page(page)
        except PageNotAnInteger:
            transactions = paginator.page(1)
        except EmptyPage:
            transactions = paginator.page(paginator.num_pages)

        context['transactions'] = transactions
        return context

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

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'finance/budget_list.html', {'budgets': budgets})

@login_required
def set_active_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    Budget.objects.filter(user=request.user).update(is_active=False)
    budget.is_active = True
    budget.save()
    return redirect('dashboard')

@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BudgetForm(instance=budget, user=request.user)
    return render(request, 'finance/edit_budget.html', {'form': form})

@login_required
def summary(request):
    user_budget = Budget.objects.filter(user=request.user).first()
    transactions = Transaction.objects.filter(user=request.user)
    form = SummaryFilterForm(request.GET or None, user=request.user)

    if form.is_valid():
        # Filtro por fechas
        date_range = form.cleaned_data['date_range']
        
        if date_range == 'custom':
            if form.cleaned_data['start_date'] and form.cleaned_data['end_date']:
                transactions = transactions.filter(
                    created_at__date__gte=form.cleaned_data['start_date'],
                    created_at__date__lte=form.cleaned_data['end_date']
                )
        elif date_range != 'all':
            days = int(date_range)
            start_date = timezone.now() - timedelta(days=days) 
            transactions = transactions.filter(created_at__gte=start_date)
        
        # Filtro por tipo de transacción
        transaction_type = form.cleaned_data['transaction_type']
        if transaction_type != 'all':
            transactions = transactions.filter(transaction_type=transaction_type)
        
        # Filtros por categorías
        if form.cleaned_data.get('income_source'):
            transactions = transactions.filter(income_source=form.cleaned_data['income_source'])
        if form.cleaned_data.get('basic_expense'):
            transactions = transactions.filter(basic_expense=form.cleaned_data['basic_expense'])
        if form.cleaned_data.get('wish_expense'):
            transactions = transactions.filter(wish_expense=form.cleaned_data['wish_expense'])
        if form.cleaned_data.get('savings_investment'):
            transactions = transactions.filter(savings_investment=form.cleaned_data['savings_investment'])

    # Calcular totales y convertirlos a float
    total_income = float(transactions.filter(income_source__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0)
    total_basic_expenses = float(transactions.filter(basic_expense__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0)
    total_wish_expenses = float(transactions.filter(wish_expense__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0)
    total_savings_investments = float(transactions.filter(savings_investment__isnull=False).aggregate(Sum('amount'))['amount__sum'] or 0)

    # Calcular porcentajes
    percentage_basic_expenses = (total_basic_expenses / float(user_budget.basic_expenses)) * 100 if user_budget.basic_expenses > 0 else 0
    percentage_wish_expenses = (total_wish_expenses / float(user_budget.wish_expenses)) * 100 if user_budget.wish_expenses > 0 else 0
    percentage_savings_investments = (total_savings_investments / float(user_budget.savings_investments)) * 100 if user_budget.savings_investments > 0 else 0

    # Calcular saldos restantes
    remaining_basic_expenses = float(user_budget.basic_expenses) - total_basic_expenses
    remaining_wish_expenses = float(user_budget.wish_expenses) - total_wish_expenses
    remaining_savings_investments = float(user_budget.savings_investments) - total_savings_investments

    # Datos mensuales
    monthly_data = transactions.annotate(month=TruncMonth('created_at')).values('month').annotate(
        total_income=Sum('amount', filter=Q(income_source__isnull=False)),
        total_basic_expenses=Sum('amount', filter=Q(basic_expense__isnull=False)),
        total_wish_expenses=Sum('amount', filter=Q(wish_expense__isnull=False)),
        total_savings_investments=Sum('amount', filter=Q(savings_investment__isnull=False))
    ).order_by('month')

    # Formatear las fechas y convertir Decimal a float
    formatted_monthly_data = []
    for data in monthly_data:
        data['month'] = data['month'].strftime('%Y-%m')  # Formato: Año-Mes
        data['total_income'] = float(data['total_income'] or 0)
        data['total_basic_expenses'] = float(data['total_basic_expenses'] or 0)
        data['total_wish_expenses'] = float(data['total_wish_expenses'] or 0)
        data['total_savings_investments'] = float(data['total_savings_investments'] or 0)
        formatted_monthly_data.append(data)

    # Distribución del presupuesto
    budget_distribution = {
        'Gastos Básicos': float(user_budget.basic_expenses),
        'Deseos': float(user_budget.wish_expenses),
        'Ahorros/Inversiones': float(user_budget.savings_investments),
    }

    # Balance neto
    total_expenses = total_basic_expenses + total_wish_expenses + total_savings_investments
    net_balance = total_income - total_expenses

    context = {
        'total_income': total_income,
        'total_basic_expenses': total_basic_expenses,
        'total_wish_expenses': total_wish_expenses,
        'total_savings_investments': total_savings_investments,
        'user_budget': user_budget,
        'percentage_basic_expenses': percentage_basic_expenses,
        'percentage_wish_expenses': percentage_wish_expenses,
        'percentage_savings_investments': percentage_savings_investments,
        'remaining_basic_expenses': remaining_basic_expenses,
        'remaining_wish_expenses': remaining_wish_expenses,
        'remaining_savings_investments': remaining_savings_investments,
        'monthly_data': formatted_monthly_data,
        'budget_distribution': budget_distribution,
        'net_balance': net_balance,
        'form': form,
    }
    return render(request, 'finance/summary.html', context)


@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="financial_summary.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Tipo', 'Origen de Ingreso', 'Gasto Básico', 'Deseo', 'Ahorro/Inversión', 'Monto'])

    transactions = Transaction.objects.filter(user=request.user)
    form = SummaryFilterForm(request.GET, user=request.user)
    
    if form.is_valid():
        date_range = form.cleaned_data['date_range']
        
        if date_range == 'custom':
            if form.cleaned_data['start_date'] and form.cleaned_data['end_date']:
                transactions = transactions.filter(
                    created_at__date__gte=form.cleaned_data['start_date'],
                    created_at__date__lte=form.cleaned_data['end_date']
                )
        elif date_range != 'all':
            days = int(date_range)
            start_date = timezone.now() - timedelta(days=days)
            transactions = transactions.filter(created_at__gte=start_date)
        
        # Filtro por tipo de transacción
        transaction_type = form.cleaned_data['transaction_type']
        if transaction_type != 'all':
            transactions = transactions.filter(transaction_type=transaction_type)
        
        # Filtros por categorías
        if form.cleaned_data.get('income_source'):
            transactions = transactions.filter(income_source=form.cleaned_data['income_source'])
        if form.cleaned_data.get('basic_expense'):
            transactions = transactions.filter(basic_expense=form.cleaned_data['basic_expense'])
        if form.cleaned_data.get('wish_expense'):
            transactions = transactions.filter(wish_expense=form.cleaned_data['wish_expense'])
        if form.cleaned_data.get('savings_investment'):
            transactions = transactions.filter(savings_investment=form.cleaned_data['savings_investment'])
    
    # Escribir datos filtrados
    for transaction in transactions.order_by('-created_at'):
        writer.writerow([
            transaction.created_at.strftime('%Y-%m-%d'),
            transaction.get_transaction_type_display(),
            str(transaction.income_source) if transaction.income_source else '',
            str(transaction.basic_expense) if transaction.basic_expense else '',
            str(transaction.wish_expense) if transaction.wish_expense else '',
            str(transaction.savings_investment) if transaction.savings_investment else '',
            transaction.amount
        ])
    
    return response


@login_required
def export_pdf(request):
    """Exporta las transacciones filtradas en formato PDF."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_summary.pdf"'
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)
    
    # Aplicar los mismos filtros que en export_csv
    transactions = Transaction.objects.filter(user=request.user)
    form = SummaryFilterForm(request.GET, user=request.user)
    
    if form.is_valid():
        # Filtro por fechas
        date_range = form.cleaned_data['date_range']
        
        if date_range == 'custom':
            if form.cleaned_data['start_date'] and form.cleaned_data['end_date']:
                transactions = transactions.filter(
                    created_at__date__gte=form.cleaned_data['start_date'],
                    created_at__date__lte=form.cleaned_data['end_date']
                )
        elif date_range != 'all':
            days = int(date_range)
            start_date = timezone.now() - timedelta(days=days)
            transactions = transactions.filter(created_at__gte=start_date)
        
        # Filtro por tipo de transacción
        transaction_type = form.cleaned_data['transaction_type']
        if transaction_type != 'all':
            transactions = transactions.filter(transaction_type=transaction_type)
        
        # Filtros por categorías
        if form.cleaned_data.get('income_source'):
            transactions = transactions.filter(income_source=form.cleaned_data['income_source'])
        if form.cleaned_data.get('basic_expense'):
            transactions = transactions.filter(basic_expense=form.cleaned_data['basic_expense'])
        if form.cleaned_data.get('wish_expense'):
            transactions = transactions.filter(wish_expense=form.cleaned_data['wish_expense'])
        if form.cleaned_data.get('savings_investment'):
            transactions = transactions.filter(savings_investment=form.cleaned_data['savings_investment'])
    
    # Encabezado del PDF con información de filtros
    p.drawString(100, 800, "Resumen Financiero - Filtros Aplicados")
    p.drawString(100, 780, f"Fecha: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    
    if form.is_valid():
        filter_info = []
        if form.cleaned_data['date_range'] != 'all':
            filter_info.append(f"Rango: {form.cleaned_data['date_range']}")
        if form.cleaned_data['transaction_type'] != 'all':
            filter_info.append(f"Tipo: {form.cleaned_data['transaction_type']}")
        # Agregar más filtros si es necesario
        
        if filter_info:
            p.drawString(100, 760, "Filtros: " + ", ".join(filter_info))
    
    # Tabla de transacciones
    p.drawString(50, 730, "Fecha")
    p.drawString(120, 730, "Tipo")
    p.drawString(180, 730, "Descripción")
    p.drawString(400, 730, "Monto")
    p.line(50, 725, 550, 725)
    
    y = 710
    for transaction in transactions.order_by('-created_at'):
        description = ""
        if transaction.income_source:
            description = f"Ingreso: {transaction.income_source}"
        elif transaction.basic_expense:
            description = f"Gasto Básico: {transaction.basic_expense}"
        elif transaction.wish_expense:
            description = f"Deseo: {transaction.wish_expense}"
        elif transaction.savings_investment:
            description = f"Ahorro: {transaction.savings_investment}"
        
        p.drawString(50, y, transaction.created_at.strftime('%Y-%m-%d'))
        p.drawString(120, y, transaction.get_transaction_type_display())
        p.drawString(180, y, description)
        p.drawString(400, y, f"${transaction.amount:.2f}")
        
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 750
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
def module_list(request):
    modules = Module.objects.all().order_by("order")
    progress = {p.module.id: p.completed for p in UserProgress.objects.filter(user=request.user)}
    return render(request, "recursos_educativos/module_list.html", {"modules": modules, "progress": progress})

@login_required
def module_detail(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    progress, _ = UserProgress.objects.get_or_create(user=request.user, module=module)
    previous_module = Module.objects.filter(order=module.order - 1).first()
    if previous_module:
        previous_completed = UserProgress.objects.filter(user=request.user, module=previous_module, completed=True).exists()
        if not previous_completed:
            messages.error(request, "Error: Debes completar el módulo anterior antes de acceder a este.")
            return redirect("module_list")
    return render(request, "recursos_educativos/module_detail.html", {"module": module, "progress": progress})

@login_required
def complete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    progress, _ = UserProgress.objects.get_or_create(user=request.user, module=module)
    progress.completed = True
    progress.save()

    next_module = Module.objects.filter(order=module.order + 1).first()
    if next_module:
        return redirect("module_detail", module_id=next_module.id)
    return render(request, "recursos_educativos/finished.html")