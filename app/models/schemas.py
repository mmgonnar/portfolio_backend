from pydantic import BaseModel, EmailStr  # type: ignore[import-not-found]
from typing import Optional


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    phone_extension: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str
    architecture: str
    technical_details: str
    image_url: str
    logo_url: Optional[str] = None
    repository_url: Optional[str] = None
    live_url: Optional[str] = None
    technologies: list[str]
    created_at: str
