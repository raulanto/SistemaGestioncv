# en mi_app/templatetags/unfold_helpers.py

from django import template
from django.utils.html import format_html
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def render_estado_badge(estado_valor, estado_display):
    """
    Renderiza un badge de estado del proyecto usando el helper de Unfold.
    """

    # 1. Tu misma lógica de configuración de color
    estados_config = {
        'EJECUCION': {
            'color': 'primary',
        },
        'PAUSADO': {
            'color': 'danger',
        },
        'FINALIZADO': {
            'color': 'succes',
        },
        'PLAN': {  # 'PLAN' o cualquier otro por defecto
            'color': 'warning',
        }
    }

    # 2. Obtenemos la configuración (con un 'default' seguro)
    config = estados_config.get(estado_valor, estados_config['PLAN'])

    # 3. Preparamos el contexto para el helper
    context = {
        'text': estado_display,
        'type': config['color'],
    }

    # 4. Renderizamos el helper label.html
    html_badge = render_to_string(
        "unfold/helpers/label.html",
        context
    )

    return format_html("{}", html_badge)