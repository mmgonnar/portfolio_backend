import logging
import os

from fastapi import FastAPI, Query  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from app.features.projects.service import ProjectService
from app.models.schemas import ContactMessage

from app.features.contact.service import ContactService
from app.features.briefs.router import router as brief_router

# Sin esta configuracion los logger.* de la app no emiten nada, porque el
# logger raiz queda en WARNING por defecto. LOG_LEVEL es opcional.
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "https://www.mmgonnar.com",
    "https://mmgonnar.com",
    "https://portfolio-backend-tarb.onrender.com",
]

# Los despliegues de vista previa de Vercel tienen un host distinto en cada
# commit, asi que no se pueden listar. El patron cubre las dos formas que usa
# Vercel para este proyecto:
#   portfolio-<hash>-<scope>.vercel.app
#   portfolio-git-<rama>-<scope>.vercel.app
#
# Deliberadamente NO es todo vercel.app: exige el prefijo "portfolio-", que es
# el nombre del proyecto, y ancla ambos extremos. El segmento intermedio no
# admite puntos, de modo que algo como portfolio-x.vercel.app.otrodominio.com
# no entra. Produccion sigue en la lista explicita de arriba.
VERCEL_PREVIEW_ORIGIN = r"^https://portfolio-[a-z0-9-]+\.vercel\.app$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=VERCEL_PREVIEW_ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brief_router, prefix="/api/v1", tags=["Brief"])


@app.get("/")
def home():
    return {"message": "API ready"}


@app.post("/contact")
def send_message(msg: ContactMessage):
    # No se registra el nombre ni el mensaje: son datos personales y los logs
    # de Render se conservan.
    return ContactService.submit_contact(msg)


@app.get("/projects")
def get_projects(lang: str = Query("es", description="Language: es or en")):
    return ProjectService.list_projects(lang=lang)
