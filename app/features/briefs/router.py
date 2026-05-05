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
    phone: str = Form(""),
    company: str = Form(""),
    projectName: str = Form(""),
    projectType: str = Form(...),
    projectDescription: str = Form(...),
    hasExistingSite: bool = Form(False),
    existingSiteUrl: str = Form(""),
    features: str = Form(...),
    featuresDetail: str = Form(""),
    targetAudience: str = Form(""),
    competitors: str = Form(""),
    visualStyle: str = Form(""),
    visualReferences: str = Form(""),
    brandColors: str = Form(""),
    brandAssetsReady: bool = Form(False),
    budget: str = Form(...),
    timeline: str = Form(...),
    flexibleBudget: bool = Form(False),
    additionalNotes: str = Form(""),
    locale: str = Form("en"),
    referenceLinks: str = Form(""),
    attachments: List[UploadFile] = File(None),
    supabase: Client = Depends(get_supabase),
):
    try:
        # 1. Procesar datos
        try:
            features_list = json.loads(features) if features else []
        except json.JSONDecodeError:
            features_list = features.split(",") if features else []

        # Build data_to_save with default values for BriefSubmission
        project_type_value = projectType if projectType else "website"
        budget_value = budget if budget else "not_defined"
        timeline_value = timeline if timeline else "flexible"

        data_to_save = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "projectName": projectName or company,
            "projectType": project_type_value,
            "projectDescription": projectDescription,
            "hasExistingSite": hasExistingSite,
            "existingSiteUrl": existingSiteUrl,
            "features": features_list,
            "featuresDetail": featuresDetail,
            "targetAudience": targetAudience,
            "competitors": competitors,
            "visualStyle": visualStyle,
            "visualReferences": visualReferences,
            "brandColors": brandColors or False,
            "brandAssetsReady": brandAssetsReady,
            "budget": budget_value,
            "timeline": timeline_value,
            "flexibleBudget": flexibleBudget,
            "additionalNotes": additionalNotes,
            "locale": locale,
            "referenceLinks": referenceLinks,
        }

        # 2. Guardar en Supabase
        supabase_data = {
            "client_name": name,
            "client_email": email,
            "client_phone": phone,
            "company": company,
            "project_name": projectName or company,
            "project_type": project_type_value,
            "budget": budget_value,
            "timeline": timeline_value,
            "locale": locale,
            "full_data": data_to_save,
        }
        
        # Filter out empty strings for optional fields
        supabase_data = {k: v for k, v in supabase_data.items() if v}
        
        try:
            res = supabase.table("design_briefs").insert(supabase_data).execute()
        except Exception as supabase_err:
            # Fallback: insert only required fields
            print(f"⚠️ Supabase insert error: {supabase_err}")
            try:
                res = supabase.table("design_briefs").insert({
                    "client_name": name,
                    "client_email": email,
                    "project_type": project_type_value,
                    "full_data": data_to_save,
                }).execute()
            except Exception as e2:
                logger.error(f"Supabase fallback also failed: {e2}")
                # Still fail but with clearer error
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error: {str(e2)}",
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