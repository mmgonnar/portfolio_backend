from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.features.projects.service import ProjectService
from app.models.schemas import ContactMessage

from app.features.contact.service import ContactService

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "https://www.mmgonnar.com",
    "https://portfolio-backend-tarb.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "API ready"}

@app.post("/contact")
def send_message(msg: ContactMessage):
    print(f"Mensaje de {msg.name}: {msg.message}")
    return ContactService.submit_contact(msg)

@app.get("/projects")
def get_projects():
    return ProjectService.list_projects()