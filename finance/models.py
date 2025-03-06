from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=[('gasto', 'Gasto'), ('ingreso', 'Ingreso')])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} - {self.category.name}"

class Income(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} - {self.category.name}"

class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Presupuesto inicial
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)  # Saldo actual
    basic_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wish_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_investments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Para saber cuándo fue la última actualización

    def save(self, *args, **kwargs):
        total_amount = Decimal(self.total_amount)

        self.basic_expenses = total_amount * Decimal('0.5')
        self.wish_expenses = total_amount * Decimal('0.3')
        self.savings_investments = total_amount * Decimal('0.2')

        if self.current_balance <= total_amount * Decimal('0.15'):
            print(f"⚠️ Alerta: Tu saldo está por debajo del 15% del presupuesto inicial ({total_amount * Decimal('0.15'):.2f})")

        super().save(*args, **kwargs)

    def update_balance_with_income(self, amount):
        """Sumar un ingreso y actualizar presupuesto y porcentajes"""
        self.current_balance += Decimal(amount)
        self.total_amount = self.current_balance  # Ahora el presupuesto se actualiza
        self.basic_expenses = self.total_amount * Decimal('0.5')
        self.wish_expenses = self.total_amount * Decimal('0.3')
        self.savings_investments = self.total_amount * Decimal('0.2')
        self.save()

    def update_balance_with_expense(self, amount):
        """Restar un gasto al saldo actual"""
        self.current_balance -= Decimal(amount)
        self.save()

    def is_balance_low(self):
        """Verifica si el saldo está por debajo del 15% del presupuesto inicial"""
        threshold = self.total_amount * Decimal('0.15')
        return self.current_balance <= threshold

    def __str__(self):
        return f"Presupuesto de {self.user.username}: {self.total_amount}"

class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='resources/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class TransactionHistory(models.Model):
    TRANSACTION_TYPES = [
        ('create', 'Creación'),
        ('update', 'Actualización'),
        ('delete', 'Eliminación'),
    ]
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.TextField()  # Detalles del cambio

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_date}"
    
class IncomeSource(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class BasicExpense(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class WishExpense(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class SavingsInvestment(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Ingreso'),
        ('expense', 'Gasto'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount}"

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