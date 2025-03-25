from django.db import migrations
from django.utils import timezone
from datetime import timedelta
import random

def create_final_transactions(apps, schema_editor):
    # Modelos
    Transaction = apps.get_model('finance', 'Transaction')
    User = apps.get_model('auth', 'User')
    Budget = apps.get_model('finance', 'Budget')
    
    # Obtener usuario y presupuesto
    user = User.objects.get(username='rafa')
    budget = Budget.objects.get(user=user)  # Asegúrate que existe
    
    # Datos de ejemplo mejorados
    transactions = [
        {
            'name': 'Salario Enero',
            'amount': 2500.00,
            'type': 'income',
            'days_ago': 30,
            'desc': 'Pago mensual nómina'
        },
        # Más transacciones...
    ]
    
    # Generar 100 transacciones variadas
    today = timezone.now()
    for i in range(100):
        trans_type = random.choice(['income', 'expense', 'savings'])
        
        if trans_type == 'income':
            name = f"Ingreso {random.choice(['Salario', 'Freelance', 'Bono'])}"
            amount = round(random.uniform(800, 3000), 2)
        elif trans_type == 'expense':
            name = f"Gasto {random.choice(['Comida', 'Transporte', 'Servicios'])}"
            amount = round(random.uniform(50, 500), 2)
        else:
            name = f"Ahorro {random.choice(['Emergencia', 'Inversión'])}"
            amount = round(random.uniform(200, 1000), 2)
        
        Transaction.objects.create(
            user=user,
            budget=budget,
            name=f"{name} #{i+1}",
            amount=amount,
            transaction_type=trans_type,
            description=f"Transacción de ejemplo #{i+1}",
            created_at=today - timedelta(days=random.randint(1, 180))
        )

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0005_populate_transactions'),  # Reemplaza con tu última migración real
    ]

    operations = [
        migrations.RunPython(create_final_transactions),
    ]