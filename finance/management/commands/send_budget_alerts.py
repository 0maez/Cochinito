from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from finance.models import Budget
from django.db.models import Sum

class Command(BaseCommand):
    help = "Envía alertas por correo y notificaciones internas sobre el estado del presupuesto."

    def handle(self, *args, **options):
        budgets = Budget.objects.all()
        for budget in budgets:
            user = budget.user
            alerts = []

            # 1. Saldo total inferior al 20%
            threshold_20 = budget.total_amount * Decimal('0.20')
            if budget.current_balance < threshold_20:
                subject = "Alerta: Saldo bajo"
                message = (
                    f"Hola {user.username},\n\n"
                    f"Tu saldo actual ({budget.current_balance:.2f}) es menor al 20% de tu presupuesto total ({budget.total_amount:.2f}).\n"
                    "¡Recuerda que es momento de ahorrar!."
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                alerts.append("Saldo total inferior al 20%")

            # 2. Gastos básicos excedidos (saldo disponible negativo)
            if budget.available_basic < Decimal('0.00'):
                subject = "Alerta: Gastos básicos excedidos"
                message = (
                    f"Hola {user.username},\n\n"
                    f"Los gastos básicos han excedido lo asignado ({budget.total_amount * Decimal('0.5'):.2f}).\n"
                    "Revisa tus gastos básicos para mantener el control de tu presupuesto."
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                alerts.append("Gastos básicos excedidos")

            # 3. Gastos de deseo excedidos
            if budget.available_wish < Decimal('0.00'):
                subject = "Alerta: Gastos de deseo excedidos"
                message = (
                    f"Hola {user.username},\n\n"
                    f"Los gastos de deseo han excedido lo asignado ({budget.total_amount * Decimal('0.3'):.2f}).\n"
                    "¡Controla tus deseos!"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                alerts.append("Gastos de deseo excedidos")

            if alerts:
                self.stdout.write(self.style.SUCCESS(f"Alertas enviadas a {user.email}: {', '.join(alerts)}"))
