from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from finance.models import Reminder
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class Command(BaseCommand):
    help = 'Envía notificaciones a los usuarios sobre recordatorios de pago próximos'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        # Buscar recordatorios de pago que vencen en 5 días o el mismo día
        reminders = Reminder.objects.filter(
            date__in=[today, today + timedelta(days=5)],
            is_paid=False
        )

        for reminder in reminders:
            user_email = reminder.user.email  # Asegúrate de que el usuario tiene un correo válido
            if user_email:
                subject = f"🔔 Recordatorio de pago: {reminder.name}"
                message = (
                    f"Hola {reminder.user.username},\n\n"
                    f"Este es un recordatorio de que tu pago de '{reminder.name}' "
                    f"vence el {reminder.date}. No olvides realizar tu pago a tiempo.\n\n"
                    f"Gracias por usar AlcanciaApp 🐷."
                )
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,  # Remitente
                    [user_email],  # Destinatario
                    fail_silently=False,
                )

                self.stdout.write(self.style.SUCCESS(f"Correo enviado a {user_email} para el pago de {reminder.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Usuario {reminder.user.username} no tiene email registrado."))
