import logging
import os
import json
from typing import List, Optional
from functools import lru_cache

# Importaciones de FastAPI
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Form, File, UploadFile # type: ignore[import-not-found]
from supabase import create_client, Client # type: ignore[import-not-found]
from app.models.brief import BriefSubmission

# Importaciones de tu app
from app.features.briefs.service import BriefService

logger = logging.getLogger(__name__)
router = APIRouter()

@lru_cache
def get_supabase() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL y SUPABASE_KEY son requeridas")
    return create_client(url, key)

@router.post("/send-brief")
async def handle_brief(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    email: str = Form(...),
    projectName: str = Form(...),
    projectType: str = Form(...),
    description: str = Form(...),
    budget: str = Form(...),
    timeline: str = Form(...),
    features: str = Form(...), 
    referenceLinks: str = Form(""),
    additionalNotes: str = Form(""),
    attachments: List[UploadFile] = File(None),
    supabase: Client = Depends(get_supabase),
):
    try:
        # 1. Procesar datos
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

        # 2. Guardar en Supabase
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

        brief_id = res.data[0]["id"]
        print(f"✅ Supabase OK — ID: {brief_id}")

        # 3. Generar PDF + Enviar correo 
        # IMPORTANTE: Pasamos data_to_save porque 'brief' (Pydantic) ya no se usa aquí
        brief_object = BriefSubmission(**data_to_save)

        print("⏳ Llamando BriefService.submit_brief...")
        result = BriefService.submit_brief(brief_object)
        print(f"✅ BriefService OK — {result}")

        return {
            "status": "success",
            "message": result.get("message", "Brief guardado correctamente"),
            "id": brief_id,
        }

    except Exception as e:
        logger.error(f"Error guardando brief: {str(e)}")
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )