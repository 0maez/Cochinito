from django.db import migrations

def create_terminos(apps, schema_editor):
    Modulo = apps.get_model('finance', 'Modulo')
    TerminoBasico = apps.get_model('finance', 'TerminoBasico')

    # Módulo 1: Presupuesto Personal
    modulo1 = Modulo.objects.get(orden=1)
    TerminoBasico.objects.create(
        modulo=modulo1,
        termino="Presupuesto",
        descripcion="Un plan que organiza tus ingresos y gastos para alcanzar metas financieras. Ayuda a evitar deudas y ahorrar para el futuro."
    )
    TerminoBasico.objects.create(
        modulo=modulo1,
        termino="Ingresos",
        descripcion="Dinero que recibes (salario, bonos, ingresos extras, etc.)."
    )
    TerminoBasico.objects.create(
        modulo=modulo1,
        termino="Gastos",
        descripcion="Dinero que gastas en necesidades (alquiler, comida, transporte) y deseos (entretenimiento, lujos)."
    )
    TerminoBasico.objects.create(
        modulo=modulo1,
        termino="Ahorro",
        descripcion="Parte de tus ingresos que reservas para metas futuras o emergencias."
    )
    TerminoBasico.objects.create(
        modulo=modulo1,
        termino="Balance",
        descripcion="Diferencia entre ingresos y gastos. Debe ser positivo para ahorrar o invertir."
    )

    # Módulo 2: Ahorro e Inversión Básica
    modulo2 = Modulo.objects.get(orden=2)
    TerminoBasico.objects.create(
        modulo=modulo2,
        termino="Ahorro",
        descripcion="Guardar dinero para metas a corto o largo plazo (ej: vacaciones, jubilación)."
    )
    TerminoBasico.objects.create(
        modulo=modulo2,
        termino="Inversión",
        descripcion="Usar dinero para generar más dinero (ej: acciones, fondos de inversión, bienes raíces)."
    )
    TerminoBasico.objects.create(
        modulo=modulo2,
        termino="Interés Simple",
        descripcion="Interés calculado solo sobre el monto inicial invertido o prestado."
    )
    TerminoBasico.objects.create(
        modulo=modulo2,
        termino="Interés Compuesto",
        descripcion="Interés calculado sobre el monto inicial más los intereses acumulados. Es clave para el crecimiento del dinero a largo plazo."
    )
    TerminoBasico.objects.create(
        modulo=modulo2,
        termino="Riesgo y Rentabilidad",
        descripcion="A mayor rentabilidad esperada, mayor riesgo de perder dinero."
    )

    # Módulo 3: Deudas y Créditos
    modulo3 = Modulo.objects.get(orden=3)
    TerminoBasico.objects.create(
        modulo=modulo3,
        termino="Deuda",
        descripcion="Dinero que debes a alguien (bancos, tarjetas de crédito, préstamos)."
    )
    TerminoBasico.objects.create(
        modulo=modulo3,
        termino="Tipos de Deuda",
        descripcion="Deuda buena: Inversión que genera valor (ej: préstamo para educación). Deuda mala: Gastos que no generan valor (ej: tarjetas de crédito para compras innecesarias)."
    )
    TerminoBasico.objects.create(
        modulo=modulo3,
        termino="Tasa de Interés",
        descripcion="Porcentaje que se cobra por pedir dinero prestado."
    )
    TerminoBasico.objects.create(
        modulo=modulo3,
        termino="Pago Mínimo",
        descripcion="Cantidad mínima que debes pagar en una tarjeta de crédito para evitar multas, pero no reduce la deuda rápidamente."
    )
    TerminoBasico.objects.create(
        modulo=modulo3,
        termino="Amortización",
        descripcion="Proceso de pagar una deuda en cuotas que incluyen capital e intereses."
    )

    # Módulo 4: Educación Financiera para Emprendedores
    modulo4 = Modulo.objects.get(orden=4)
    TerminoBasico.objects.create(
        modulo=modulo4,
        termino="Costos Fijos",
        descripcion="Gastos que no cambian con el nivel de producción (ej: alquiler, salarios)."
    )
    TerminoBasico.objects.create(
        modulo=modulo4,
        termino="Costos Variables",
        descripcion="Gastos que dependen del nivel de producción (ej: materias primas, comisiones)."
    )
    TerminoBasico.objects.create(
        modulo=modulo4,
        termino="Punto de Equilibrio",
        descripcion="Nivel de ventas donde los ingresos igualan los costos (no hay ganancias ni pérdidas)."
    )
    TerminoBasico.objects.create(
        modulo=modulo4,
        termino="Flujo de Caja",
        descripcion="Dinero que entra y sale de un negocio en un período determinado. Es clave para mantener la liquidez."
    )
    TerminoBasico.objects.create(
        modulo=modulo4,
        termino="Margen de Ganancia",
        descripcion="Diferencia entre el precio de venta y el costo de producción. Se expresa como porcentaje del precio de venta."
    )

def delete_terminos(apps, schema_editor):
    TerminoBasico = apps.get_model('tu_app', 'TerminoBasico')
    TerminoBasico.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_terminobasico'),  # Asegúrate de cambiar 'tu_app' y el nombre de la migración previa
    ]

    operations = [
        migrations.RunPython(create_terminos, delete_terminos),
    ]
