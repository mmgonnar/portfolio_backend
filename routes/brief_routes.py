from fastapi import APIRouter, HTTPException  # type: ignore[import-not-found]
from app.models.brief import BriefSubmission
from supabase import create_client  # type: ignore[import-not-found]
import os

router = APIRouter()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

@router.post('/send-brief')
async def handle_brief(brief:BriefSubmission):
    try:
        data_to_save = brief.dict()

        res = supabase.table('design_briefs').insert({
            'client_name': brief.name,
            'client_email': brief.email,
            'project_name': brief.projectName,
            'full_data': data_to_save
        }).execute()
        return {"status": "success", "message": "¡Brief guardado!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con la DB: {str(e)}")