import logging
from typing import List

# Importaciones de FastAPI
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Form, File, UploadFile
from pydantic import EmailStr
from supabase import Client
from app.features.briefs.labels import TIMELINE_LABELS, label
from app.models.brief import BriefSubmission, ScopeLevel

# Importaciones de tu app
from app.db.supabase_client import get_supabase
from app.features.briefs.service import BriefService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/send-brief")
async def handle_brief(
    background_tasks: BackgroundTasks,
    # Topes de longitud en la frontera HTTP, no en BriefSubmission: el modelo
    # se construye DESPUES del insert, asi que un tope ahi llegaria tarde. Un
    # campo pasado de largo es 422 antes de guardar o enviar nada. Bandas:
    # name 100 (igual que el zod del frontend), texto corto 200, texto largo
    # 5000, URLs 2048 (200 cortaria enlaces reales de Figma o de un sitio).
    name: str = Form(..., max_length=100),
    # EmailStr, igual que /contact: un correo malformado es 422 antes de tocar
    # la base. El formulario ya valida con zod, esto cubre el POST directo.
    email: EmailStr = Form(...),
    phone: str = Form("", max_length=200),
    company: str = Form("", max_length=200),
    projectName: str = Form("", max_length=200),
    projectType: str = Form(..., max_length=200),
    projectDescription: str = Form(..., max_length=5000),
    hasExistingSite: bool = Form(False),
    existingSiteUrl: str = Form("", max_length=2048),
    features: List[str] = Form(...),
    featuresDetail: str = Form("", max_length=5000),
    targetAudience: str = Form("", max_length=5000),
    competitors: str = Form("", max_length=5000),
    visualStyle: str = Form("", max_length=200),
    visualReferences: str = Form("", max_length=5000),
    brandColors: str = Form("", max_length=200),
    brandAssetsReady: str = Form("false", max_length=200),
    designStatus: str = Form("", max_length=200),
    designLink: str = Form("", max_length=2048),
    wantsDesignQuote: str = Form("false", max_length=200),
    scopeLevel: str = Form("", max_length=200),
    scopeWeight: str = Form("", max_length=200),
    budget: str = Form(..., max_length=200),
    timeline: str = Form(..., max_length=200),
    flexibleBudget: str = Form("false", max_length=200),
    currency: str = Form("USD", max_length=200),
    additionalNotes: str = Form("", max_length=5000),
    locale: str = Form("en", max_length=200),
    attachments: List[UploadFile] = File(None),
    supabase: Client = Depends(get_supabase),
):
    # Se registra la forma de la peticion, nunca su contenido: nombre, email y
    # descripcion son datos personales y los logs se conservan.
    logger.info(
        "Brief recibido: tipo=%s features=%d adjuntos=%d alcance=%s/%s",
        projectType,
        len(features),
        len(attachments) if attachments else 0,
        scopeLevel or "-",
        scopeWeight or "-",
    )

    try:
        # 1. Procesar datos
        # El formulario repite la clave "features", una vez por seleccion, y
        # FastAPI las agrupa en una lista. Un cliente que mande JSON o una
        # cadena separada por comas no es soportado: debe repetir la clave.
        features_list = [f for f in features if f and f.strip()]

        # El alcance lo calcula el frontend (scope.ts es la unica copia de los
        # pesos), aqui solo se valida la forma: nivel conocido y peso entero no
        # negativo. Un valor que no cuadra se guarda vacio en vez de romper el
        # envio, porque el brief del cliente vale mas que la estimacion.
        scope_level_value = scopeLevel if scopeLevel in ScopeLevel.__members__ else None
        if scopeLevel and scope_level_value is None:
            logger.warning("scopeLevel desconocido, se ignora: %s", scopeLevel)

        scope_weight_value = None
        if scopeWeight:
            try:
                parsed_weight = int(scopeWeight)
                scope_weight_value = parsed_weight if parsed_weight >= 0 else None
            except ValueError:
                scope_weight_value = None
            if scope_weight_value is None:
                logger.warning("scopeWeight invalido, se ignora: %s", scopeWeight)

        wants_design_quote_value = str(wantsDesignQuote).lower() == "true"

        # Build data_to_save with default values for BriefSubmission
        project_type_value = projectType if projectType else "website"
        budget_value = budget if budget else "not_defined"
        timeline_value = timeline if timeline else "flexible"
        currency_value = currency if currency else "USD"

        # Convert budget key to display value based on currency
        # Mismas bandas que features/brief/utils/scope.ts en el frontend.
        budget_ranges = {
            "USD": {
                "r1": "Menos de $1,200 USD",
                "r2": "$1,200 - $3,000 USD",
                "r3": "$3,000 - $6,000 USD",
                "r4": "$6,000+ USD",
            },
            "MXN": {
                "r1": "Menos de $15,000 MXN",
                "r2": "$15,000 - $40,000 MXN",
                "r3": "$40,000 - $80,000 MXN",
                "r4": "$80,000+ MXN",
            },
        }
        budget_display = budget_ranges.get(currency_value, {}).get(budget_value, budget_value) or budget_value

        # Las etiquetas viven en labels.py, que es lo que tambien usan el PDF
        # y el correo. Este mapa tenia cuatro entradas y le faltaba
        # one_3_months, que el modelo si acepta.
        timeline_display = label(timeline_value, TIMELINE_LABELS)

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
            "designStatus": designStatus,
            "designLink": designLink,
            "wantsDesignQuote": wants_design_quote_value,
            "scopeLevel": scope_level_value,
            "scopeWeight": scope_weight_value,
            "budget": budget_display,
            "timeline": timeline_display,
            "flexibleBudget": flexibleBudget if isinstance(flexibleBudget, bool) else (flexibleBudget.lower() == "true" if isinstance(flexibleBudget, str) else False),
            "currency": currency_value,
            "additionalNotes": additionalNotes,
            "locale": locale,
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
            "design_status": designStatus if designStatus else None,
            "design_link": designLink if designLink else None,
            "wants_design_quote": wants_design_quote_value,
            "scope_level": scope_level_value,
            "scope_weight": scope_weight_value,
            "full_data": data_to_save,
        }
        
        # Filter out None values only (keep False booleans)
        supabase_data = {k: v for k, v in supabase_data.items() if v is not None}
        
        # Sin fallback: si el insert completo falla, el error es ruidoso. El
        # fallback de 4 campos guardaba filas casi vacias con un 200, asi que
        # un error de esquema pasaba como exito y el brief se perdia a medias.
        try:
            res = supabase.table("design_briefs").insert(supabase_data).execute()
        except Exception:
            logger.exception("Insert de design_briefs fallo")
            raise HTTPException(
                status_code=500,
                detail="No se pudo guardar el brief. Por favor intenta mas tarde",
            )

        brief_id = res.data[0]["id"]
        logger.info("Brief guardado en Supabase: id=%s", brief_id)

        # 2.5. Store file names for PDF (files are sent via email without reading here)
        file_names = []
        if attachments:
            attachments_list = attachments if isinstance(attachments, list) else [attachments]
            for f in attachments_list:
                if f and hasattr(f, 'filename') and f.filename:
                    file_names.append(f.filename)

        # Add file names to data_to_save for PDF
        data_to_save["files"] = file_names if file_names else None

        # 3. Generar PDF + Enviar correo
        # La fila ya existe: un fallo del PDF o del correo despues de guardar
        # no debe volver como 500, porque el cliente reintentaria y duplicaria
        # el brief. Igual que /contact, se registra el error sin datos
        # personales y se responde exito.
        message = "Brief recibido. Te contactaré pronto."
        try:
            brief_object = BriefSubmission(**data_to_save)
            result = await BriefService.submit_brief(brief_object, attachments)
            message = result.get("message", message)
            logger.info("Brief procesado: id=%s", brief_id)
        except Exception:
            logger.exception("Brief guardado pero el correo fallo: id=%s", brief_id)

        return {
            "status": "success",
            "message": message,
            "id": brief_id,
        }

    except HTTPException:
        # Ya tiene un mensaje generico propio, no se vuelve a envolver.
        raise
    except Exception:
        # El detalle completo va al log del servidor, al cliente solo un
        # mensaje generico: el texto de la excepcion puede revelar nombres de
        # tablas o columnas de Supabase.
        logger.exception("Error guardando brief")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor. Por favor intenta mas tarde",
        )