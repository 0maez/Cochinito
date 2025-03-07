from django.core.management.base import BaseCommand
from finance.models import Reminder
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Envía notificaciones a los usuarios sobre recordatorios de pago próximos'

    def handle(self, *args, **kwargs):
        # Obtén la fecha actual
        today = timezone.now().date()

        # Filtra los recordatorios que tienen la fecha de pago en los próximos 7 días
        reminders = Reminder.objects.filter(
            date__gte=today,
            date__lte=today + timedelta(days=7),
            is_paid=False
        )

        # Enviar notificaciones a los usuarios
        for reminder in reminders:
            # Aquí puedes enviar el correo o la notificación
            # Por ejemplo, usando reminder.user.email para enviar un correo
            self.stdout.write(f"Recordatorio enviado a {reminder.user.email} para el pago de {reminder.name}")
