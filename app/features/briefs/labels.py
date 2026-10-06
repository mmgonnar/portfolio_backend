"""Traduce las claves que manda el frontend a etiquetas legibles en espanol.

El PDF y el correo son para Mariela, no para el cliente, asi que siempre van en
espanol sin importar el locale del brief.

Las filas viejas de design_briefs guardan el titulo ya traducido en vez de la
clave ('Gestion de Contenidos', 'Pasarela de Pagos'), y hay claves que ya no
existen en el formulario nuevo. Por eso cada busqueda cae de vuelta al valor
original: un brief de hace meses se sigue leyendo igual.
"""

PROJECT_TYPE_LABELS = {
    "website": "Sitio web",
    "web_app": "Aplicacion web",
    "landing": "Landing page",
    "redesign": "Rediseno",
    "dashboard": "Dashboard / panel de administracion",
    "other": "Otro",
    # Tipo retirado, se conserva para las filas que ya lo tienen.
    "wordpress": "Sitio en Wordpress",
}

FEATURE_LABELS = {
    "auth": "Cuentas de usuario",
    "admin_dashboard": "Panel de administracion",
    "forms_emails": "Formularios y correo",
    "database": "Base de datos",
    "integrations": "Integraciones",
    "seo": "Configuracion SEO",
    "multi_language": "Varios idiomas",
    "deployment": "Despliegue y dominio",
    # Funcionalidades retiradas, siguen apareciendo en briefs anteriores.
    "cms": "Gestion de contenidos",
    "payments": "Pasarela de pagos",
    "analytics": "Analytics y seguimiento",
    "mobile": "Diseno mobile-first",
}

DESIGN_STATUS_LABELS = {
    "ready": "Ya tiene el diseno listo",
    "brand_kit": "Tiene kit de marca",
    "none": "No tiene nada todavia",
}

SCOPE_LEVEL_LABELS = {
    "basic": "Basico",
    "medium": "Medio",
    "advanced": "Avanzado",
}

VISUAL_STYLE_LABELS = {
    "minimal": "Minimal",
    "luxury": "Elegante",
    "editorial": "Editorial",
    "brutalist": "Brutalista",
    "darkLuxury": "Lujoso",
    "modern": "Moderno",
}

TIMELINE_LABELS = {
    "asap": "Lo antes posible",
    "one_month": "1 mes",
    "one_3_months": "1 a 3 meses",
    "two_three_months": "2 a 3 meses",
    "flexible": "Flexible",
}


def label(value, mapping: dict) -> str:
    """Devuelve la etiqueta de una clave, o el valor tal cual si no la conoce."""
    if value is None:
        return ""
    text = value.value if hasattr(value, "value") else str(value)
    return mapping.get(text, text)


def feature_labels(features) -> list:
    """Mapea una lista de claves de funcionalidad a etiquetas legibles."""
    if not features:
        return []
    return [label(feature, FEATURE_LABELS) for feature in features]


def scope_summary(level, weight) -> str:
    """'Medio (peso 7)', o solo uno de los dos si falta el otro."""
    level_text = label(level, SCOPE_LEVEL_LABELS)
    if level_text and weight is not None:
        return f"{level_text} (peso {weight})"
    if level_text:
        return level_text
    return "" if weight is None else f"Peso {weight}"
