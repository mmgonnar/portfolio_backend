from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import List, Optional
import json
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────
# Solo ScopeLevel: los enums de tipo/presupuesto/diseño/timeline no se pueden
# usar como tipo de campo porque el frontend manda '' como estado sin elegir y
# el router lo mapea a defaults; validar contra el enum rechazaria esos envios.
class ScopeLevel(str, Enum):
    basic = "basic"
    medium = "medium"
    advanced = "advanced"


# ─── Modelo ───────────────────────────────────────────────────────────────────
class BriefSubmission(BaseModel):
    model_config = ConfigDict(extra="allow") 

    @field_validator('files', mode='before')
    @classmethod
    def parse_files(cls, v):
        if v is None or v == '':
            return []
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v if isinstance(v, list) else []

    @field_validator(
        'hasExistingSite', 'brandAssetsReady', 'flexibleBudget', 'wantsDesignQuote',
        mode='before',
    )
    @classmethod
    def parse_bool_fields(cls, v):
        if v is None or v == '':
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() == 'true'
        return False

    # Paso 1 — Contacto
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

    # Paso 2 — Proyecto
    projectType: Optional[str] = None
    projectName: Optional[str] = None
    projectDescription: Optional[str] = None
    hasExistingSite: bool = False
    existingSiteUrl: Optional[str] = None

    # Paso 3 — Features
    features: List[str] = Field(default_factory=list)
    featuresDetail: Optional[str] = None

    # Paso 4 — Estilo y audiencia
    targetAudience: Optional[str] = None
    competitors: Optional[str] = None
    visualStyle: Optional[str] = None
    visualReferences: Optional[str] = None
    brandColors: Optional[str] = None
    brandAssetsReady: bool = False

    # Diseño: que trae el cliente y si pidio cotizacion de UI/UX
    designStatus: Optional[str] = None
    designLink: Optional[str] = None
    wantsDesignQuote: bool = False

    # Alcance calculado en el frontend desde scope.ts
    scopeLevel: Optional[str] = None
    scopeWeight: Optional[int] = None

    # Paso 5 — Presupuesto
    budget: Optional[str] = None
    timeline: Optional[str] = None
    flexibleBudget: bool = False
    additionalNotes: Optional[str] = None

    # Paso 6 — Archivos
    files: List[str] = []

    # Metadata
    locale: str = "es"