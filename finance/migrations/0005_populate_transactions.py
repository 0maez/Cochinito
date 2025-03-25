# finance/migrations/0005_populate_transactions.py
from django.db import migrations
from django.utils import timezone
from datetime import timedelta
import random

def populate_transactions(apps, schema_editor):
    # Obtener modelos
    Transaction = apps.get_model('finance', 'Transaction')
    User = apps.get_model('auth', 'User')
    Budget = apps.get_model('finance', 'Budget')
    IncomeSource = apps.get_model('finance', 'IncomeSource')
    BasicExpense = apps.get_model('finance', 'BasicExpense')
    WishExpense = apps.get_model('finance', 'WishExpense')
    SavingsInvestment = apps.get_model('finance', 'SavingsInvestment')

    # Obtener usuario rafa y su presupuesto
    user = User.objects.get(username='rafa')
    budget = Budget.objects.get(user=user)  # Asume que ya existe
    
    # Obtener o crear categorías
    salary, _ = IncomeSource.objects.get_or_create(user=user, name="Salario")
    freelance = IncomeSource.objects.get_or_create(user=user, name="Freelance")[0]
    
    food = BasicExpense.objects.get_or_create(user=user, name="Comida")[0]
    transport = BasicExpense.objects.get_or_create(user=user, name="Transporte")[0]
    
    entertainment = WishExpense.objects.get_or_create(user=user, name="Entretenimiento")[0]
    travel = WishExpense.objects.get_or_create(user=user, name="Viajes")[0]
    
    emergency_fund = SavingsInvestment.objects.get_or_create(user=user, name="Fondo Emergencia")[0]
    investments = SavingsInvestment.objects.get_or_create(user=user, name="Inversiones")[0]

    # Plantillas de transacciones
    transactions_data = [
        # Ingresos (15 ejemplos)
        {'type': 'income', 'name': "Pago nómina", 'amount': 2500, 'date_offset': 5, 'income_source': salary},
        {'type': 'income', 'name': "Diseño freelance", 'amount': 800, 'date_offset': 15, 'income_source': freelance},
        
        # Gastos básicos (20 ejemplos)
        {'type': 'expense', 'name': "Supermercado", 'amount': 350, 'date_offset': 2, 'basic_expense': food},
        {'type': 'expense', 'name': "Gasolina", 'amount': 150, 'date_offset': 3, 'basic_expense': transport},
        
        # Gastos deseos (10 ejemplos)
        {'type': 'expense', 'name': "Cine", 'amount': 120, 'date_offset': 10, 'wish_expense': entertainment},
        
        # Ahorros (5 ejemplos)
        {'type': 'savings', 'name': "Ahorro mensual", 'amount': 500, 'date_offset': 1, 'savings_investment': emergency_fund}
    ]

    # Generar más transacciones con variaciones
    today = timezone.now()
    transactions = []
    
    for data in transactions_data:
        # Transacción base
        transactions.append(Transaction(
            user=user,
            budget=budget,
            name=data['name'],
            amount=data['amount'],
            transaction_type=data['type'],
            description=f"Transacción de {data['type']}: {data['name']}",
            created_at=today - timedelta(days=data['date_offset']),
            **{data['type']+'_source': data.get(data['type']+'_source')}  # Asigna la FK correspondiente
        ))
        
        # Variaciones (5 por cada tipo)
        for i in range(1, 6):
            variation = data.copy()
            variation['amount'] = round(data['amount'] * random.uniform(0.8, 1.2), 2)
            variation['date_offset'] = data['date_offset'] + random.randint(1, 30)
            
            transactions.append(Transaction(
                user=user,
                budget=budget,
                name=f"{data['name']} #{i}",
                amount=variation['amount'],
                transaction_type=data['type'],
                description=f"Variación {i} de {data['name']}",
                created_at=today - timedelta(days=variation['date_offset']),
                **{data['type']+'_source': data.get(data['type']+'_source')}
            ))

    # Insertar todas las transacciones
    Transaction.objects.bulk_create(transactions)
    print(f"Se crearon {len(transactions)} transacciones para el usuario 'rafa'")

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0004_alter_transaction_created_at'),  # Asegúrate que coincide con tu última migración
    ]

    operations = [
        migrations.RunPython(populate_transactions),
    ]