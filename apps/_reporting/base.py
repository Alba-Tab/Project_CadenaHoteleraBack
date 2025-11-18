from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Sequence

#Qué hace: define ReportField, ReportDefinition y un ReportRegistry para cada app.

ReportFormat = Literal["xlsx", "docx", "pdf"]

@dataclass(frozen=True)
class ReportField:
    key: str
    label: str
    type: Literal["int", "str", "decimal", "date", "datetime", "bool"]
    ops: Sequence[str]

@dataclass(frozen=True)
class ReportDefinition:
    slug: str
    name: str
    model_path: str
    default_ordering: Sequence[str]
    columns: Sequence[ReportField]
    filterable: Sequence[ReportField]
    description: Optional[str] = None

class ReportRegistry:
    def __init__(self) -> None:
        self._reg: Dict[str, ReportDefinition] = {}

    def register(self, definition: ReportDefinition) -> None:
        if definition.slug in self._reg:
            raise ValueError(f"Reporte duplicado: {definition.slug}")
        self._reg[definition.slug] = definition

    def get(self, slug: str) -> ReportDefinition:
        try:
            return self._reg[slug]
        except KeyError:
            raise KeyError(f"Reporte '{slug}' no existe")

    def all(self) -> List[ReportDefinition]:
        return list(self._reg.values())