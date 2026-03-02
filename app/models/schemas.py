from pydantic import BaseModel, EmailStr  # type: ignore[import-not-found]
from typing import Optional

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    phone_extension: Optional[str] = None

class Projects(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    image_url: str
    tech_stack: list[str]
    github_url: Optional[str] = None
    demo_url: Optional[str] = None