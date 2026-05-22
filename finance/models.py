from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,)
    age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class BasicExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class WishExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SavingsInvestment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)
    basic_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wish_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_investments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.is_active:  # Solo si este presupuesto se marca como activo
            Budget.objects.filter(user=self.user).exclude(pk=self.pk).update(is_active=False)
        total = Decimal(self.total_amount)
        
        if not self.pk:
            if self.current_balance is None:
                self.current_balance = total
        self.basic_expenses = total * Decimal('0.5')
        self.wish_expenses = total * Decimal('0.3')
        self.savings_investments = total * Decimal('0.2')

        Budget.objects.filter(user=self.user).update(is_active=False)
        self.is_active = True  

        if self.current_balance <= total * Decimal('0.20'):
            print(f"⚠️ Alerta: Tu saldo está por debajo del 20% del presupuesto inicial ({total * Decimal('0.20'):.2f})")

        super().save(*args, **kwargs)

    def update_balance_with_income(self, amount):
        self.current_balance += Decimal(amount)
        self.save(update_fields=['current_balance'])

    def update_balance_with_expense(self, amount):
        self.current_balance -= Decimal(amount)
        self.save(update_fields=['current_balance'])
    
    def update_balance_with_savings(self, amount):
        self.current_balance -= Decimal(amount)
        self.save(update_fields=['current_balance'])

    def is_balance_low(self):
        threshold = self.total_amount * Decimal('0.20')
        return self.current_balance <= threshold
    
    def total_basic_spent(self):
        return sum(t.amount for t in self.transaction_set.filter(basic_expense__isnull=False))

    def total_wish_spent(self):
        return sum(t.amount for t in self.transaction_set.filter(wish_expense__isnull=False))
    
    def total_savings_spent(self):
        return sum(t.amount for t in self.transaction_set.filter(savings_investment__isnull=False))

    @property
    def available_basic(self):
        basic_spent = self.transaction_set.filter(
            transaction_type='expense',
            basic_expense__isnull=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        allocated = self.total_amount * Decimal('0.5')
        return allocated - basic_spent

    @property
    def available_wish(self):
        wish_spent = self.transaction_set.filter(
            transaction_type='expense',
            wish_expense__isnull=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        allocated = self.total_amount * Decimal('0.3')
        return allocated - wish_spent

    @property
    def available_savings(self):
        savings_spent = self.transaction_set.filter(
            transaction_type='savings',
            savings_investment__isnull=False
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        allocated = self.total_amount * Decimal('0.2')
        return allocated - savings_spent

    def __str__(self):
        return f"Presupuesto de {self.user.username}: {self.total_amount}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
        ('savings', 'Ahorro'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Sin nombre")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)    
    income_source = models.ForeignKey('IncomeSource', on_delete=models.SET_NULL, null=True, blank=True)
    basic_expense = models.ForeignKey('BasicExpense', on_delete=models.SET_NULL, null=True, blank=True)
    wish_expense = models.ForeignKey('WishExpense', on_delete=models.SET_NULL, null=True, blank=True)
    savings_investment = models.ForeignKey('SavingsInvestment', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.budget_id:  # Si no tiene presupuesto asignado
            active_budget = Budget.objects.filter(user=self.user, is_active=True).first()
            if not active_budget:
                raise ValidationError("No hay un presupuesto activo para asociar esta transacción.")
            self.budget = active_budget
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.description} ({self.amount})"

@receiver(pre_save, sender=Transaction)
def capture_transaction_before_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Transaction.objects.get(pk=instance.pk)
            instance._old_amount = old.amount
            instance._old_type = old.transaction_type
        except Transaction.DoesNotExist:
            instance._old_amount = None
            instance._old_type = None
    else:
        instance._old_amount = None
        instance._old_type = None

@receiver(post_save, sender=Transaction)
def update_budget_on_transaction(sender, instance, created, **kwargs):
    budget = instance.budget

    if created:
        if instance.transaction_type == 'income':
            budget.current_balance += instance.amount
        elif instance.transaction_type == 'expense':
            budget.current_balance -= instance.amount
        elif instance.transaction_type == 'savings':
            budget.current_balance -= instance.amount
    else:
        if hasattr(instance, '_old_amount') and instance._old_amount is not None:
            if instance._old_type == 'income':
                budget.current_balance -= instance._old_amount
            elif instance._old_type == 'expense':
                budget.current_balance += instance._old_amount
            elif instance._old_type == 'savings':
                budget.current_balance += instance._old_amount

            if instance.transaction_type == 'income':
                budget.current_balance += instance.amount
            elif instance.transaction_type == 'expense':
                budget.current_balance -= instance.amount
            elif instance.transaction_type == 'savings':
                budget.current_balance -= instance.amount

    budget.save()

@receiver(post_delete, sender=Transaction)
def update_budget_on_transaction_delete(sender, instance, **kwargs):
    budget = instance.budget
    if instance.transaction_type == 'income':
        budget.current_balance -= instance.amount
    elif instance.transaction_type == 'expense':
        budget.current_balance += instance.amount
    elif instance.transaction_type == 'savings':
        budget.current_balance += instance.amount    
    budget.save()

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.date}"
        
class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Module(models.Model):
    title = models.CharField(max_length=255)  
    description = models.TextField()  
    video_title = models.CharField(max_length=255)  
    video_url = models.URLField()  
    exercise_instructions = models.TextField(null=True, blank=True, help_text="Ingrese cada instruccion en una nueva linea")  
    exercise_objective = models.CharField(null=True, blank=True, max_length=255)  
    order = models.IntegerField(unique=True)  

    def __str__(self):
        return self.title
    def __str__(self):
        return self.title

class BasicTerm(models.Model):
    module = models.ForeignKey(Module, related_name="terms", on_delete=models.CASCADE)  
    term = models.CharField(max_length=255)  

    def __str__(self):
        return f"{self.term} ({self.module.title})"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    module = models.ForeignKey(Module, on_delete=models.CASCADE)  
    completed = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} - {self.module.title} - {'Completed' if self.completed else 'Pending'}"