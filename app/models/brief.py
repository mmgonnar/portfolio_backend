from pydantic import BaseModel, EmailStr, Field, ConfigDict  # type: ignore[import-not-found]
from typing   import List, Optional
from enum     import Enum

# ─── Enums ────────────────────────────────────────────────────────────────────
class ProjectType(str, Enum):
    website   = 'website'
    ecommerce = 'ecommerce'
    landing   = 'landing'
    webapp    = 'webapp'
    redesign  = 'redesign'
    other     = 'other'

class VisualStyle(str, Enum):
    minimalist = 'minimalist'
    bold       = 'bold'
    corporate  = 'corporate'
    playful    = 'playful'
    elegant    = 'elegant'
    tech       = 'tech'
    not_sure   = 'not_sure'

class BudgetRange(str, Enum):
    under_1k     = 'under_1k'
    range_1k_3k  = '1k_3k'
    range_3k_5k  = '3k_5k'
    range_5k_10k = '5k_10k'
    over_10k     = 'over_10k'
    not_defined  = 'not_defined'

class Timeline(str, Enum):
    asap           = 'asap'
    one_month      = '1_month'
    one_3_months   = '1_3_months'
    three_6_months = '3_6_months'
    flexible       = 'flexible'

# ─── Modelo ───────────────────────────────────────────────────────────────────
class BriefSubmission(BaseModel):
    model_config = ConfigDict(extra='forbid') # ✅ rechaza campos no declarados

    # Paso 1 — Contacto
    name:    str  = Field(..., min_length=2)
    email:   EmailStr
    phone:   Optional[str]  = None
    company: Optional[str]  = None
    role:    Optional[str]  = None

    # Paso 2 — Proyecto
    projectType:        ProjectType
    projectName:        str           = Field(..., min_length=2)
    projectDescription: str           = Field(..., min_length=20)
    hasExistingSite:    bool          = False
    existingSiteUrl:    Optional[str] = None

    # Paso 3 — Features
    features:       List[str]      = Field(..., min_length=1)
    featuresDetail: Optional[str]  = None

    # Paso 4 — Estilo y audiencia
    targetAudience:   str           = Field(..., min_length=10)
    competitors:      Optional[str] = None
    visualStyle:      VisualStyle
    visualReferences: Optional[str] = None
    brandColors:      bool          = False
    brandAssetsReady: bool          = False

    # Paso 5 — Presupuesto
    budget:          BudgetRange
    timeline:        Timeline
    flexibleBudget:  bool          = False
    additionalNotes: Optional[str] = None

    # Paso 6 — Archivos
    files: List[str] = Field(default_factory=list)

    # Metadata
    locale: str = 'es'