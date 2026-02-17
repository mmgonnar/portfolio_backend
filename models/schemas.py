from pydantic import BaseModel
from typing import Optional

class Project(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    link: Optional[str] = None
    technologies: List[str] = []


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str