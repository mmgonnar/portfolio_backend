import logging
from fastapi import APIRouter, HTTPException, Depends  # type: ignore[import-not-found]
from functools import lru_cache
from supabase import create_client, Client  # type: ignore[import-not-found]
from app.models.brief import BriefSubmission
from app.features.briefs.service import BriefService
import os

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
    brief: BriefSubmission,
    supabase: Client = Depends(get_supabase),
):
    print("🔥 ENDPOINT EJECUTADO")
    # ✅ SIN try/except temporalmente — veremos el error real en la terminal

    # ── 1. Guardar en Supabase ─────────────────────────────────────────
    res = (
        supabase.table("design_briefs")
        .insert(
            {
                "client_name": brief.name,
                "client_email": brief.email,
                "project_name": brief.projectName,
                "project_type": brief.projectType.value,
                "full_data": brief.model_dump(),
            }
        )
        .execute()
    )

    brief_id = res.data[0]["id"]
    print(f"✅ Supabase OK — ID: {brief_id}")

    # ── 2. Generar PDF + Enviar correo ────────────────────────────────
    print("⏳ Llamando BriefService.submit_brief...")
    result = BriefService.submit_brief(brief)
    print(f"✅ BriefService OK — {result}")

    return {
        "status": "success",
        "message": result["message"],
        "id": brief_id,
    }
