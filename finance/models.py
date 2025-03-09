from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)  
    basic_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wish_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_investments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        total_amount = Decimal(self.total_amount)
        
        if self.current_balance is None:
            self.current_balance = total_amount
        self.basic_expenses = total_amount * Decimal('0.5')
        self.wish_expenses = total_amount * Decimal('0.3')
        self.savings_investments = total_amount * Decimal('0.2')

        if self.current_balance <= total_amount * Decimal('0.15'):
            print(f"⚠️ Alerta: Tu saldo está por debajo del 15% del presupuesto inicial ({total_amount * Decimal('0.15'):.2f})")

        super().save(*args, **kwargs)

    def update_balance_with_income(self, amount):
        self.current_balance += Decimal(amount)
        self.total_amount += Decimal(amount)
        self.save()

    def update_balance_with_expense(self, amount):
        self.current_balance -= Decimal(amount)
        self.save()

    def is_balance_low(self):
        threshold = self.total_amount * Decimal('0.15')
        return self.current_balance <= threshold

    def __str__(self):
        return f"Presupuesto de {self.user.username}: {self.total_amount}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Sin nombre")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)  
    category = models.CharField(max_length=100, blank=True, null=True)  
    income_source = models.ForeignKey('IncomeSource', on_delete=models.SET_NULL, null=True, blank=True)
    basic_expense = models.ForeignKey('BasicExpense', on_delete=models.SET_NULL, null=True, blank=True)
    wish_expense = models.ForeignKey('WishExpense', on_delete=models.SET_NULL, null=True, blank=True)
    savings_investment = models.ForeignKey('SavingsInvestment', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  
            if self.transaction_type == 'income':
                if self.budget:  
                    self.budget.update_balance_with_income(self.amount)
            elif self.transaction_type == 'expense':
                if self.budget:  
                    self.budget.update_balance_with_expense(self.amount)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.description} ({self.amount})"

@receiver(post_save, sender=Transaction)
def update_budget_on_transaction(sender, instance, created, **kwargs):
    if created:
        budget = instance.budget
        if instance.transaction_type == 'income':
            budget.current_balance += instance.amount
            budget.total_amount = budget.current_balance
        elif instance.transaction_type == 'expense':
            budget.current_balance -= instance.amount

        budget.save()

from django.db import models
from django.contrib.auth.models import User


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
    image = models.ImageField(upload_to='resources/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title