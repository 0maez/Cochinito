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
        self.stdout.write(f"🕒 Iniciando envío de notificaciones - Fecha: {today}")
        
        start_date = today
        end_date = today + timedelta(days=5)
        
        reminders = Reminder.objects.filter(
            date__gte=start_date,
            date__lte=end_date,
            is_paid=False
        )
        
        self.stdout.write(f"🔍 Recordatorios encontrados: {reminders.count()}")
        
        if not reminders.exists():
            self.stdout.write(self.style.WARNING("⚠️ No hay recordatorios pendientes"))
            return

        for reminder in reminders:
            user_email = reminder.user.email
            if not user_email:
                self.stdout.write(self.style.WARNING(f"⛔ Usuario {reminder.user.username} sin email"))
                continue

            subject = f"🔔 Recordatorio de pago: {reminder.name}"
            message = (
                f"Hola {reminder.user.username},\n\n"
                f"Tu pago de '{reminder.name}' vence el {reminder.date}.\n"
                "Realiza tu pago a tiempo para evitar inconvenientes.\n\n"
                "Gracias por usar AlcancíApp 🐷."
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Corregido aquí
                [user_email],
                fail_silently=False
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Correo enviado a {user_email}"))

        self.stdout.write(self.style.SUCCESS("🎉 Proceso completado"))