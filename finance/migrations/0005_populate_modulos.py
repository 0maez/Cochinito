from django.db import migrations

def agregar_modulos(apps, schema_editor):
    Modulo = apps.get_model('finance', 'Modulo') 
    modulos_data = [
        {
            "titulo": "Presupuesto Personal",
            "descripcion": "Aprende a gestionar tus ingresos y gastos.",
            "video_titulo": "¿Qué es un presupuesto y cómo hacerlo?",
            "video_url": "https://www.youtube.com/watch?v=YzZQ6zX9_hc",
            "ejercicio": "Descarga la plantilla de presupuesto y llena tus ingresos y gastos.",
            "orden": 1
        },
        {
            "titulo": "Ahorro e Inversión Básica",
            "descripcion": "Descubre el poder del interés compuesto.",
            "video_titulo": "El interés compuesto y por qué es importante",
            "video_url": "https://www.youtube.com/watch?v=wf91rEGw88Q",
            "ejercicio": "Calcula cuánto ahorrarás en 5 años con un interés del 5%.",
            "orden": 2
        },
        {
            "titulo": "Deudas y Créditos",
            "descripcion": "Cómo manejar deudas y tarjetas de crédito.",
            "video_titulo": "Cómo manejar tus deudas y tarjetas de crédito",
            "video_url": "https://www.youtube.com/watch?v=6eT2Z8Z8Z8I",
            "ejercicio": "Prioriza tus deudas según la tasa de interés.",
            "orden": 3
        },
        {
            "titulo": "Educación Financiera para Emprendedores",
            "descripcion": "Conoce los conceptos clave para emprender.",
            "video_titulo": "Conceptos básicos de finanzas para emprendedores",
            "video_url": "https://www.youtube.com/watch?v=6eT2Z8Z8Z8I",
            "ejercicio": "Calcula cuántas tazas de café necesitas vender para cubrir costos.",
            "orden": 4
        }
    ]
    
    for data in modulos_data:
        Modulo.objects.create(**data)

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0004_modulo_progresousuario'),  # Ahora depende de la 0004
    ]

    operations = [
        migrations.RunPython(agregar_modulos),
    ]
