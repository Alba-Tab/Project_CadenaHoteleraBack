from typing import Any, Dict, Iterable, List
from django.apps import apps
from django.db.models import Model, QuerySet

from .base import ReportDefinition

#Qué hace: traduce {field, op, value} → lookups Django, con lista blanca.

OP_LOOKUPS = {
    "eq": "exact",
    "ne": "exact",          # vía exclude
    "contains": "contains",
    "icontains": "icontains",
    "gte": "gte",
    "lte": "lte",
    "between": "range",
    "in": "in",
    "isnull": "isnull",
}

# def import_model(model_path: str) -> type[Model]:
#     """'apps.reservas.models.Reserva' → Modelo."""
#     app_label, _, model_name = model_path.rpartition(".models.")
#     return apps.get_model(app_label, model_name)

def import_model(model_path: str):
    """
    Acepta 'apps.reservas.models.Reserva' y resuelve el app_label correcto ('reservas').
    Si algún app usa un label custom, también lo localiza.
    """
    app_module, sep, model_name = model_path.rpartition(".models.")
    if not sep or not model_name:
        raise ValueError('model_path debe ser "paquete.app.models.Modelo"')

    # 1) Candidato por convención: último segmento del módulo => label
    app_label_candidate = app_module.split(".")[-1]

    try:
        return apps.get_model(app_label_candidate, model_name)
    except LookupError:
        # 2) Fallback: buscar AppConfig cuyo .name == app_module y usar su .label real
        for cfg in apps.get_app_configs():
            if cfg.name == app_module:
                return apps.get_model(cfg.label, model_name)
        # Si no se encuentra, relanzar el error original
        raise

def apply_filters(qs: QuerySet, definition: ReportDefinition, raw_filters: Iterable[Dict[str, Any]]) -> QuerySet:
    allowed = {f.key for f in definition.filterable}
    for f in raw_filters or []:
        field = f.get("field")
        op = f.get("op")
        value = f.get("value", None)
        if field not in allowed or op not in OP_LOOKUPS:
            continue

        lookup = OP_LOOKUPS[op]
        if op == "ne":
            qs = qs.exclude(**{f"{field}__exact": value})
        elif op == "between":
            if isinstance(value, list) and len(value) == 2:
                qs = qs.filter(**{f"{field}__{lookup}": (value[0], value[1])})
        elif op == "isnull":
            qs = qs.filter(**{f"{field}__{lookup}": bool(value)})
        else:
            qs = qs.filter(**{f"{field}__{lookup}": value})
    return qs

def project_columns(qs: QuerySet, columns: List[str]):
    return list(qs.values(*columns))