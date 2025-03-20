from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum

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
    basic_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wish_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    savings_investments = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        total = Decimal(self.total_amount)
        if self.current_balance is None:
            self.current_balance = total

        self.basic_expenses = total * Decimal('0.5')
        self.wish_expenses = total * Decimal('0.3')
        self.savings_investments = total * Decimal('0.2')

        if self.current_balance <= total * Decimal('0.15'):
            print(f"⚠️ Alerta: Tu saldo está por debajo del 15% del presupuesto inicial ({total * Decimal('0.15'):.2f})")

        super().save(*args, **kwargs)

    def update_balance_with_income(self, amount):
        self.current_balance += Decimal(amount)
        self.total_amount += Decimal(amount)
        self.save()

    def update_balance_with_expense(self, amount):
        self.current_balance -= Decimal(amount)
        self.save()
    
    def update_balance_with_savings(self, amount):
        self.current_balance -= Decimal(amount)
        self.save()

    def is_balance_low(self):
        threshold = self.total_amount * Decimal('0.15')
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
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
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
        elif instance.transaction_type == 'savings':
            budget.current_balance -= instance.amount
        budget.save()

@receiver(post_delete, sender=Transaction)
def update_budget_on_transaction_delete(sender, instance, **kwargs):
    budget = instance.budget
    if instance.transaction_type == 'income':
        budget.current_balance -= instance.amount
        budget.total_amount -= instance.amount
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
    
class Modulo(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    video_titulo = models.CharField(max_length=255)
    video_url = models.URLField()
    ejercicio_instrucciones = models.TextField(null=True, blank=True, help_text="Ingrese cada instrucción en una nueva línea.")
    ejercicio_objetivo = models.CharField(null=True, blank=True, max_length=255)
    orden = models.IntegerField(unique=True)  

    def __str__(self):
        return self.titulo

class TerminoBasico(models.Model):
    modulo = models.ForeignKey(Modulo, related_name="terminos", on_delete=models.CASCADE)
    termino = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.termino} ({self.modulo.titulo})"

class ProgresoUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.modulo.titulo} - {'Completado' if self.completado else 'Pendiente'}"    