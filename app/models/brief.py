from pydantic import BaseModel, EmailStr, Field, ConfigDict  # type: ignore[import-not-found]
from typing import List, Optional
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

    # Paso 1 — Contacto
    name: str = Field(..., min_length=2)
    email: EmailStr
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
    files: List[str] = Field(default_factory=list)

    # Metadata
    locale: str = "es"
