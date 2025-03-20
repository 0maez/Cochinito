from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Devuelve el valor del diccionario para la clave dada."""
    return dictionary.get(key)
