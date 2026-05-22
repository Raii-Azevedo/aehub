from django import template

register = template.Library()


@register.filter
def split(value, arg=','):
    """Divide uma string pelo separador informado."""
    if not value:
        return []
    return [part.strip() for part in str(value).split(arg) if part.strip()]


@register.filter
def strip(value):
    """Remove espaços em branco das bordas."""
    return str(value).strip() if value else ''
