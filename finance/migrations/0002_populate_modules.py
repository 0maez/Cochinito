from django.db import migrations

def agregar_modulos(apps, schema_editor):
    Module = apps.get_model('finance', 'Module') 
    modulos_data = [
        {
            "title": "Presupuesto Personal",
            "description": "Aprende a gestionar tus ingresos y gastos.",
            "video_title": "Cómo hacer tu presupuesto personal",
            "video_url": "https://www.youtube.com/watch?v=kmi6EugSR0E",
            "exercise_instructions": """
            1. Identifica tus ingresos: Anota todas las fuentes de ingreso.
            2. Registra tus gastos: Clasifícalos en fijos y variables.
            3. Establece metas de ahorro: Define cuánto deseas ahorrar.
            4. Analiza y ajusta: Revisa si tus gastos están alineados con tus metas.
            """,
            "exercise_objective": "Aprender a gestionar tus finanzas personales mediante la planificación y el control de ingresos y gastos, estableciendo metas de ahorro alcanzables.",
            "order": 1
        },
        {
            "title": "Ahorro e Inversión Básica",
            "description": "Descubre el poder del ahorro y la inversión.",
            "video_title": "CLASE 1 - Conceptos básicos sobre ahorro e inversión",
            "video_url": "https://www.youtube.com/watch?v=mOnhcibusH8",
            "exercise_instructions": """
            1. Establece una meta de ahorro específica.
            2. Calcula el monto mensual necesario para alcanzar tu meta.
            3. Investiga opciones de inversión según tu perfil de riesgo.
            4. Diseña un plan de acción financiero.
            """,
            "exercise_objective": "Comprender la relación entre ahorro e inversión y cómo establecer metas financieras alcanzables.",
            "order": 2
        },
        {
            "title": "Deudas y Créditos",
            "description": "Aprende a manejar deudas y tarjetas de crédito de manera efectiva.",
            "video_title": "Te muestro cómo manejo mi dinero: Ingresos, gastos, ahorro e inversiones",
            "video_url": "https://www.youtube.com/watch?v=EgK9LhtKL3o",
            "exercise_instructions": """
            1. Enumera todas tus deudas actuales.
            2. Ordena tus deudas según la tasa de interés.
            3. Diseña una estrategia de pago (método bola de nieve o avalancha).
            4. Evalúa opciones para reducir tasas de interés.
            """,
            "exercise_objective": "Desarrollar habilidades para gestionar deudas y créditos de manera estratégica.",
            "order": 3
        },
        {
            "title": "Educación Financiera para Emprendedores",
            "description": "Conceptos clave para la gestión financiera en emprendimientos.",
            "video_title": "Educación Financiera para Principiantes: El Camino Hacia la Libertad Financiera",
            "video_url": "https://www.youtube.com/watch?v=n1PfwEXnwTY",
            "exercise_instructions": """
            1. Calcula cuántos productos debes vender para cubrir costos.
            2. Analiza la estructura de costos de un pequeño negocio.
            3. Identifica fuentes de financiamiento para emprendedores.
            """,
            "exercise_objective": "Aprender sobre la planificación financiera para emprendimientos y estrategias de financiamiento.",
            "order": 4
        },
        {
            "title": "Planificación Financiera a Largo Plazo",
            "description": "Aprende a gestionar tus finanzas a largo plazo.",
            "video_title": "APRENDE A GESTIONAR TU DINERO (Curso Finanzas Personales)",
            "video_url": "https://www.youtube.com/watch?v=TETvAxrPfW0",
            "exercise_instructions": """
            1. Define una estrategia de inversión a largo plazo.
            2. Establece objetivos financieros a 10 años.
            3. Evalúa planes de jubilación y seguros.
            """,
            "exercise_objective": "Comprender la importancia de la planificación financiera a largo plazo y sus beneficios.",
            "order": 5
        },
        {
            "title": "Gestión de Riesgos Financieros",
            "description": "Aprende a mitigar riesgos en tus finanzas personales y empresariales.",
            "video_title": "Educación Financiera para Principiantes y Expertos",
            "video_url": "https://www.youtube.com/playlist?list=PL6AQmhIr6GK0kCk53Xl3I_T7Sdord-XGN",
            "exercise_instructions": """
            1. Identifica riesgos financieros personales y empresariales.
            2. Evalúa estrategias de mitigación de riesgos.
            3. Investiga sobre seguros y fondos de emergencia.
            """,
            "exercise_objective": "Desarrollar estrategias para gestionar y minimizar riesgos financieros.",
            "order": 6
        }
    ]
    
    for data in modulos_data:
        Module.objects.create(**data)

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(agregar_modulos),
    ]
