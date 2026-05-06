from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict  # type: ignore[import-not-found]
from typing import List, Optional, Union
import json
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────
class ProjectType(str, Enum):
    website = "website"
    wordpress = "wordpress"
    landing = "landing"
    webapp = "webapp"
    redesign = "redesign"
    other = "other"


class BudgetRange(str, Enum):
    r1 = "r1"
    r2 = "r2"
    r3 = "r3"
    r4 = "r4"
    r5 = "r5"
    not_defined = "not_defined"


class Timeline(str, Enum):
    asap = "asap"
    one_month = "one_month"
    one_3_months = "one_3_months"
    two_three_months = "two_three_months"
    flexible = "flexible"


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
            except:
                return []
        return v if isinstance(v, list) else []

    @field_validator('hasExistingSite', 'brandAssetsReady', 'flexibleBudget', mode='before')
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

    # Paso 5 — Presupuesto
    budget: Optional[str] = None
    timeline: Optional[str] = None
    flexibleBudget: bool = False
    additionalNotes: Optional[str] = None

    # Paso 6 — Archivos
    files: List[str] = []

    # Metadata
    locale: str = "es"