from app.utils.pdf_generator import generate_brief_pdf

from app.models.brief import BriefSubmission
from supabase import create_client, Client  # type: ignore[import-not-found]
import os
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Form, File, UploadFile  # type: ignore[import-not-found]
from typing import List, Optional
import json

import logging

from functools import lru_cache

from app.models.brief import BriefSubmission
import os

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Dependencia de Supabase ──────────────────────────────────────────────────
@lru_cache
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL y SUPABASE_KEY son requeridas")
    return create_client(url, key)


# ─── Endpoint ─────────────────────────────────────────────────────────────────
@router.post("/send-brief")
async def handle_brief(
    background_tasks: BackgroundTasks,
    # Recibimos cada campo como Form
    name: str = Form(...),
    email: str = Form(...),
    projectName: str = Form(...),
    projectType: str = Form(...),
    description: str = Form(...),
    budget: str = Form(...),
    timeline: str = Form(...),
    features: str = Form(...), 
    referenceLinks: Optional[str] = Form(""),
    additionalNotes: Optional[str] = Form(""),
    attachments: List[UploadFile] = File(None),
    supabase: Client = Depends(get_supabase),
):
    try:
   
        features_list = json.loads(features)


        data_to_save = {
            "name": name,
            "email": email,
            "projectName": projectName,
            "projectType": projectType,
            "description": description,
            "features": features_list,
            "budget": budget,
            "timeline": timeline,
            "referenceLinks": referenceLinks,
            "additionalNotes": additionalNotes,
        }

        res = (
            supabase.table("design_briefs")
            .insert({
                "client_name": name,
                "client_email": email,
                "project_name": projectName,
                "project_type": projectType,
                "full_data": data_to_save,
            })
            .execute()
        )

        # 4. Manejo de archivos (Opcional)
        if attachments:
            for file in attachments:
                logger.info(f"Archivo recibido: {file.filename}")
                # Aquí podrías subirlo a Supabase Storage si lo necesitas

        background_tasks.add_task(generate_brief_pdf, data_to_save)

        return {
            "status": "success",
            "message": "Brief guardado correctamente",
            "id": res.data[0]["id"],
        }

    except Exception as e:
        logger.error(f"Error guardando brief: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")