from django.db import migrations, transaction
from decimal import Decimal
from datetime import datetime, timedelta
import random

def populate_transactions(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Budget = apps.get_model('finance', 'Budget')
    Transaction = apps.get_model('finance', 'Transaction')
    IncomeSource = apps.get_model('finance', 'IncomeSource')
    BasicExpense = apps.get_model('finance', 'BasicExpense')
    WishExpense = apps.get_model('finance', 'WishExpense')
    SavingsInvestment = apps.get_model('finance', 'SavingsInvestment')

    # Obtener el usuario 'Carlos'
    user = User.objects.filter(username='Carlos').first()

    if not user:
        raise ValueError("El usuario 'Carlos' no existe.")

    # Obtener el presupuesto activo del usuario
    budget = Budget.objects.filter(user=user, is_active=True).first()

    if not budget:
        raise ValueError(f"El usuario {user.username} no tiene un presupuesto activo asignado.")

    # Obtener registros existentes
    income_sources = list(IncomeSource.objects.filter(user=user))
    basic_expenses = list(BasicExpense.objects.filter(user=user))
    wish_expenses = list(WishExpense.objects.filter(user=user))
    savings_investments = list(SavingsInvestment.objects.filter(user=user))

    # Definir probabilidades para cada tipo de transacción
    transaction_types = ['expense'] * 5 + ['income'] * 3 + ['savings'] * 2
    end_date = datetime(2025, 3, 31)  # Fecha límite: 31 de marzo de 2025
    start_date = end_date - timedelta(days=120)  # Comenzar 120 días antes (4 meses)
    transactions = []

    for _ in range(60):  # 60 transacciones en total (15 por mes en promedio)
        transaction_type = random.choice(transaction_types)
        amount = Decimal(random.randint(10, 300))  # Cantidades más variadas
        
        # Generar fecha aleatoria entre start_date y end_date
        random_days = random.randint(0, 119)
        date = start_date + timedelta(days=random_days)

        transaction_data = {
            'user': user,
            'budget': budget,
            'amount': amount,
            'transaction_type': transaction_type,
            'created_at': date,
            'description': f"Transacción generada automáticamente - {date.strftime('%d/%m/%Y')}"
        }

        if transaction_type == 'income' and income_sources:
            source = random.choice(income_sources)
            transaction_data['name'] = f'Ingreso de {source.name}'
            transaction_data['income_source'] = source
        elif transaction_type == 'expense':
            # Decidir si es gasto básico o de deseo
            if random.random() < 0.6 and basic_expenses:
                expense = random.choice(basic_expenses)
                transaction_data['name'] = f'Gasto Básico en {expense.name}'
                transaction_data['basic_expense'] = expense
            elif wish_expenses:
                expense = random.choice(wish_expenses)
                transaction_data['name'] = f'Gasto de Deseo en {expense.name}'
                transaction_data['wish_expense'] = expense
        elif transaction_type == 'savings' and savings_investments:
            investment = random.choice(savings_investments)
            transaction_data['name'] = f'Ahorro/Inversión en {investment.name}'
            transaction_data['savings_investment'] = investment

        # Solo crear la transacción si tiene un nombre válido
        if 'name' in transaction_data:
            transactions.append(Transaction(**transaction_data))

    if transactions:
        # Crear transacciones en bloques para mejor rendimiento
        with transaction.atomic():
            Transaction.objects.bulk_create(transactions)

def reverse_func(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Transaction = apps.get_model('finance', 'Transaction')

    user = User.objects.filter(username='Carlos').first()
    if user:
        Transaction.objects.filter(user=user).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0008_populate_basic_terms'),
    ]

    operations = [
        migrations.RunPython(populate_transactions, reverse_func),
    ]