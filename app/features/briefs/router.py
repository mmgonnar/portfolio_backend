import logging
import os
import json
import asyncio
from typing import List, Optional
from functools import lru_cache

# Importaciones de FastAPI
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Form, File, UploadFile # type: ignore[import-not-found]
from supabase import create_client, Client # type: ignore[import-not-found]
import json # type: ignore[import-not-found]
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
    brandAssetsReady: str = Form("false"),
    budget: str = Form(...),
    timeline: str = Form(...),
    flexibleBudget: str = Form("false"),
    currency: str = Form("USD"),
    additionalNotes: str = Form(""),
    locale: str = Form("en"),
    referenceLinks: str = Form(""),
    attachments: List[UploadFile] = File(None),
    supabase: Client = Depends(get_supabase),
):
    # DEBUG: Log incoming request
    print(f"📥 Received brief request - name: {name}, email: {email}, projectType: {projectType}")
    print(f"📥 features: {features}, budget: {budget}, currency: {currency}")
    print(f"📥 attachments: {attachments}")
    
    try:
        # 1. Procesar datos - Handle features as string or array
        try:
            # Try parsing as JSON array first
            features_list = json.loads(features) if features else []
        except json.JSONDecodeError:
            # If it's a single string, wrap in array
            if features and isinstance(features, str):
                features_list = [features]
            else:
                features_list = features.split(",") if features else []

        # Build data_to_save with default values for BriefSubmission
        project_type_value = projectType if projectType else "website"
        budget_value = budget if budget else "not_defined"
        timeline_value = timeline if timeline else "flexible"
        currency_value = currency if currency else "USD"

        # Convert budget key to display value based on currency
        budget_ranges = {
            "USD": {
                "r1": "$1K - $3K USD",
                "r2": "$3K - $5K USD",
                "r3": "$5K - $10K USD",
                "r4": "$10K - $25K USD",
                "r5": "$25K+ USD",
            },
            "MXN": {
                "r1": "$10K - $15K MXN",
                "r2": "$15K - $20K MXN",
                "r3": "$20K - $25K MXN",
                "r4": "$25K - $30K MXN",
                "r5": "$30K+ MXN",
            },
        }
        budget_display = budget_ranges.get(currency_value, {}).get(budget_value, budget_value) or budget_value

        # Convert timeline key to display value
        timeline_display = {
            "asap": "ASAP",
            "one_month": "1 Mes",
            "two_three_months": "2-3 Meses",
            "flexible": "Flexible",
        }.get(timeline_value, timeline_value)

        data_to_save = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "projectName": projectName or company,
            "projectType": project_type_value,
            "projectDescription": projectDescription,
            "hasExistingSite": hasExistingSite if isinstance(hasExistingSite, bool) else (hasExistingSite.lower() == "true" if isinstance(hasExistingSite, str) else False),
            "existingSiteUrl": existingSiteUrl,
            "features": features_list,
            "featuresDetail": featuresDetail,
            "targetAudience": targetAudience,
            "competitors": competitors,
            "visualStyle": visualStyle,
            "visualReferences": visualReferences,
            "brandColors": brandColors if brandColors else None,
            "brandAssetsReady": brandAssetsReady if isinstance(brandAssetsReady, bool) else (brandAssetsReady.lower() == "true" if isinstance(brandAssetsReady, str) else False),
            "budget": budget_display,
            "timeline": timeline_display,
            "flexibleBudget": flexibleBudget if isinstance(flexibleBudget, bool) else (flexibleBudget.lower() == "true" if isinstance(flexibleBudget, str) else False),
            "currency": currency_value,
            "additionalNotes": additionalNotes,
            "locale": locale,
            "referenceLinks": referenceLinks,
        }

        # 2. Guardar en Supabase
        supabase_data = {
            "client_name": name,
            "client_email": email,
            "client_phone": phone if phone else None,
            "company": company if company else None,
            "project_name": projectName or company or name,
            "project_type": project_type_value,
            "project_description": projectDescription if projectDescription else None,
            "has_existing_site": hasExistingSite if isinstance(hasExistingSite, bool) else (hasExistingSite.lower() == "true" if isinstance(hasExistingSite, str) else False),
            "existing_site_url": existingSiteUrl if existingSiteUrl else None,
            "features": features_list if features_list else None,
            "target_audience": targetAudience if targetAudience else None,
            "budget": budget_display,
            "timeline": timeline_display,
            "flexible_budget": flexibleBudget if isinstance(flexibleBudget, bool) else (flexibleBudget.lower() == "true" if isinstance(flexibleBudget, str) else False),
            "currency": currency_value,
            "locale": locale,
            "additional_notes": additionalNotes if additionalNotes else None,
            "full_data": data_to_save,
        }
        
        # Filter out None values only (keep False booleans)
        supabase_data = {k: v for k, v in supabase_data.items() if v is not None}
        
        print("📝 Inserting to Supabase...")
        
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

        # 2.5. Store file names for PDF (files are sent via email without reading here)
        file_names = []
        if attachments:
            attachments_list = attachments if isinstance(attachments, list) else [attachments]
            for f in attachments_list:
                if f and hasattr(f, 'filename') and f.filename:
                    file_names.append(f.filename)
                    print(f"📎 File for email: {f.filename}")

        # Add file names to data_to_save for PDF
        data_to_save["files"] = file_names if file_names else None
        
        print(f"📝 data_to_save keys: {list(data_to_save.keys())}")
        print(f"📝 files value: {data_to_save.get('files')}")

        # 3. Generar PDF + Enviar correo
        # IMPORTANTE: Pasamos data_to_save porque 'brief' (Pydantic) ya no se usa aquí
        # Also pass attachments for email
        print("📝 Creating BriefSubmission...")
        brief_object = BriefSubmission(**data_to_save)
        print(f"✅ BriefSubmission created: {brief_object.projectName}")

        print("⏳ Llamando BriefService.submit_brief...")
        result = await BriefService.submit_brief(brief_object, attachments)
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