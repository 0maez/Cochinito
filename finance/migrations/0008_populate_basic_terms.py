from django.db import migrations

def populate_basic_terms(apps, schema_editor):
    Module = apps.get_model('finance', 'Module')
    BasicTerm = apps.get_model('finance', 'BasicTerm')
    
    # Definir los términos para cada módulo. La clave es el título del módulo.
    terms_data = {
        "Presupuesto Personal": [
            "Presupuesto: Un plan que organiza tus ingresos y gastos para alcanzar metas financieras. Ayuda a evitar deudas y ahorrar para el futuro.",
            "Ingresos: Dinero que recibes (salario, bonos, ingresos extras, etc.).",
            "Gastos: Dinero que gastas en necesidades (alquiler, comida, transporte) y deseos (entretenimiento, lujos).",
            "Ahorro: Parte de tus ingresos que reservas para metas futuras o emergencias.",
            "Balance: Diferencia entre ingresos y gastos. Debe ser positivo para ahorrar o invertir.",
        ],
        "Ahorro e Inversión Básica": [
            "Ahorro: Guardar dinero para metas a corto o largo plazo (ej: vacaciones, jubilación).",
            "Inversión: Usar dinero para generar más dinero (ej: acciones, fondos de inversión, bienes raíces).",
            "Interés Simple: Interés calculado solo sobre el monto inicial invertido o prestado.",
            "Interés Compuesto: Interés calculado sobre el monto inicial más los intereses acumulados. Es clave para el crecimiento del dinero a largo plazo.",
            "Riesgo y Rentabilidad: A mayor rentabilidad esperada, mayor riesgo de perder dinero.",
        ],
        "Deudas y Créditos": [
            "Deuda: Dinero que debes a alguien (bancos, tarjetas de crédito, préstamos).",
            "Tipos de Deuda: Deuda buena: Inversión que genera valor (ej: préstamo para educación). Deuda mala: Gastos que no generan valor (ej: tarjetas de crédito para compras innecesarias).",
            "Tasa de Interés: Porcentaje que se cobra por pedir dinero prestado.",
            "Pago Mínimo: Cantidad mínima que debes pagar en una tarjeta de crédito para evitar multas, pero no reduce la deuda rápidamente.",
            "Amortización: Proceso de pagar una deuda en cuotas que incluyen capital e intereses.",
        ],
        "Educación Financiera para Emprendedores": [
            "Costos Fijos: Gastos que no cambian con el nivel de producción (ej: alquiler, salarios).",
            "Costos Variables: Gastos que dependen del nivel de producción (ej: materias primas, comisiones).",
            "Punto de Equilibrio: Nivel de ventas donde los ingresos igualan los costos (no hay ganancias ni pérdidas).",
            "Flujo de Caja: Dinero que entra y sale de un negocio en un período determinado. Es clave para mantener la liquidez.",
            "Margen de Ganancia: Diferencia entre el precio de venta y el costo de producción. Se expresa como porcentaje del precio de venta.",
        ],
        "Planificación Financiera a Largo Plazo": [
            "Planificación Financiera: Proceso de elaboración de un plan financiero integral, organizado y detallado, que garantice alcanzar los objetivos financieros determinados previamente, considerando los plazos, costes y recursos necesarios.",
            "Horizonte de Inversión: Periodo de tiempo durante el cual se espera mantener una inversión antes de necesitar el capital invertido.",
            "Tasa de Descuento: Tasa utilizada para calcular el valor presente de flujos de efectivo futuros, reflejando el costo de oportunidad del capital.",
            "Valor Presente Neto (VPN): Método de evaluación de inversiones que calcula la diferencia entre el valor presente de los ingresos y el valor presente de los costos asociados a una inversión.",
            "Diversificación: Estrategia de inversión que consiste en distribuir el capital entre diferentes activos o instrumentos financieros para reducir el riesgo total.",
        ],
        "Gestión de Riesgos Financieros": [
            "Riesgo Financiero: Posibilidad de que una empresa o individuo experimente pérdidas financieras debido a factores como fluctuaciones en los mercados, cambios en las tasas de interés o impagos de deudas.",
            "Riesgo de Mercado: Potencial de pérdidas debido a movimientos adversos en los precios de mercado, como acciones, bonos o commodities.",
            "Riesgo de Crédito: Probabilidad de que una contraparte no cumpla con sus obligaciones financieras, resultando en pérdidas para el prestamista o inversor.",
            "Riesgo de Liquidez: Riesgo de no poder vender un activo rápidamente sin incurrir en una pérdida significativa de valor.",
            "Riesgo Operacional: Peligro de pérdidas debido a fallas en procesos internos, sistemas, personas o eventos externos que afectan las operaciones de una empresa.",
            "Riesgo Legal: Posibilidad de pérdidas derivadas de acciones legales o incumplimiento de regulaciones y leyes aplicables.",
        ],
    }
    
    # Iterar sobre cada módulo y crear sus términos asociados.
    for module_title, term_list in terms_data.items():
        try:
            module = Module.objects.get(title=module_title)
        except Module.DoesNotExist:
            # Si no existe el módulo, lo saltamos.
            continue
        
        for term_text in term_list:
            BasicTerm.objects.create(module=module, term=term_text)

def remove_basic_terms(apps, schema_editor):
    BasicTerm = apps.get_model('finance', 'BasicTerm')
    BasicTerm.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0007_repopulate_data'),
    ]
    operations = [
        migrations.RunPython(populate_basic_terms, remove_basic_terms),
    ]
