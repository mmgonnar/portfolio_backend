from app.utils.pdf_generator import generate_brief_pdf
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks  # type: ignore[import-not-found]
from app.models.brief import BriefSubmission
from supabase import create_client, Client  # type: ignore[import-not-found]
import os
from functools import lru_cache

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
    brief: BriefSubmission,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase),
):
    try:
        data_to_save = brief.model_dump()  # ✅ Pydantic v2

        res = (
            supabase.table("design_briefs")
            .insert(
                {
                    "client_name": brief.name,
                    "client_email": brief.email,
                    "project_name": brief.projectName,
                    "project_type": brief.projectType.value,  # ✅ .value del enum
                    "full_data": data_to_save,
                }
            )
            .execute()
        )

        background_tasks.add_task(generate_brief_pdf, data_to_save)

        return {
            "status": "success",
            "message": "Brief guardado correctamente",
            "id": res.data[0]["id"],
        }

    except Exception as e:
        logger.error(f"Error guardando brief: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor",
        )
