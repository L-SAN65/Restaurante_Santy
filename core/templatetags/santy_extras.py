from django import template

register = template.Library()


@register.filter
def usd(value):
    """Formatea un valor numérico como moneda USD (ej. $1,234.56)."""
    try:
        return "${:,.2f}".format(float(value or 0))
    except (TypeError, ValueError):
        return "$0.00"


@register.filter
def traffic_light_class(value):
    """Mapea el semáforo (green/yellow/red) a clases de color KDS."""
    return {
        "green": "border-kds-ok text-kds-ok",
        "yellow": "border-kds-warn text-kds-warn",
        "red": "border-kds-over text-kds-over",
    }.get(value, "border-slate-400 text-slate-400")


@register.filter
def badge_class(status):
    """Clases de badge por estado de dominio."""
    mapping = {
        "disponible": "bg-mesa-disponible text-primary-deep",
        "available": "bg-mesa-disponible text-primary-deep",
        "AVAILABLE": "bg-mesa-disponible text-primary-deep",
        "reservada": "bg-blue-100 text-blue-800",
        "reserved": "bg-blue-100 text-blue-800",
        "RESERVED": "bg-blue-100 text-blue-800",
        "ocupada": "bg-amber-100 text-amber-800",
        "occupied": "bg-amber-100 text-amber-800",
        "OCCUPIED": "bg-amber-100 text-amber-800",
        "bloqueada": "bg-red-100 text-red-800",
        "blocked": "bg-red-100 text-red-800",
        "BLOCKED": "bg-red-100 text-red-800",
        "issued": "bg-primary-soft text-primary-deep",
        "ISSUED": "bg-primary-soft text-primary-deep",
        "ANNULLED": "bg-red-100 text-red-800",
        "anulada": "bg-red-100 text-red-800",
        "DRAFT": "bg-slate-100 text-slate-600",
    }
    return mapping.get(str(status), "bg-slate-100 text-slate-700")


@register.filter
def table_status_label(status):
    """Traduce el código de estado de mesa a etiqueta en español."""
    return {
        "AVAILABLE": "Disponible",
        "RESERVED": "Reservada",
        "OCCUPIED": "Ocupada",
        "BLOCKED": "Bloqueada",
    }.get(str(status), str(status))