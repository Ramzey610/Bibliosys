from django import template
from django.utils import timezone

register = template.Library()

@register.filter(name='days_until')
def days_until(value):
    """Retourne une chaîne en français du type "X jours", "1 jour" ou "Aujourd'hui".
    Si la date est dans le passé, retourne "0 jour(s)" ou le nombre négatif (préfixe '-') selon le cas.
    Accepte datetime/date objets; si la valeur est None ou invalide, retourne une chaîne vide.
    """
    if not value:
        return ''
    try:
        # Convertir en date si nécessaire
        if hasattr(value, 'date'):
            target = value.date()
        else:
            target = value
        today = timezone.localdate()
        delta = (target - today).days
    except Exception:
        return ''

    if delta == 0:
        return "Aujourd'hui"
    if delta == 1:
        return '1 jour'
    if delta > 1:
        return f'{delta} jours'
    # delta < 0
    return f"{abs(delta)} jour(s)"