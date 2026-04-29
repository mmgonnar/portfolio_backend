from pydantic import BaseModel, EmailStr  # type: ignore[import-not-found]
from typing import List, Optional, Dict, Any
from datetime import datetime

class BriefSubmission(BaseModel):
    name: str 
    email: EmailStr
    projectName: str
    projectType: str
    projectDescription: str
    features: List[str]
    targetAudience: str
    visualStyle: str
    budget: str
    timeline: str
    files: Optional[List[str]] = []
    locale: str = "es"
    class Config:
        extra = 'allow'