from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    basic_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wish_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_investments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Convertimos los valores flotantes a Decimal antes de realizar la operación
        total_amount = Decimal(self.total_amount)  # Aseguramos que sea Decimal

        self.basic_expenses = total_amount * Decimal('0.5')  # 50% para gastos básicos
        self.wish_expenses = total_amount * Decimal('0.3')   # 30% para deseos
        self.savings_investments = total_amount * Decimal('0.2')  # 20% para ahorros e inversiones

        super().save(*args, **kwargs)

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