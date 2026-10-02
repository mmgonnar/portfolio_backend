import os
import resend  # type: ignore[import-not-found]
import logging

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import UploadFile
from app.models.brief import BriefSubmission
from app.utils.pdf_generator import build_brief_filename, generate_brief_pdf

logger = logging.getLogger(__name__)


class BriefService:

    @staticmethod
    async def submit_brief(brief: BriefSubmission, attachments: List[UploadFile] = None) -> dict:
        data = brief.model_dump()

        pdf_bytes = generate_brief_pdf(data)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        pdf_name = build_brief_filename(data, suffix=stamp)
        logger.info("PDF generado en memoria: %d bytes", len(pdf_bytes))

        await BriefService._send_email(brief, pdf_bytes, pdf_name, attachments)

        return {
            "status": "success",
            "message": "Brief recibido. Te contactaré pronto.",
        }

    @staticmethod
    async def _send_email(
        brief: BriefSubmission,
        pdf_bytes: bytes,
        pdf_name: str,
        attachments: List[UploadFile] = None,
    ) -> None:
        api_key = os.environ.get("RESEND_API_KEY")

        if not api_key:
            logger.warning("RESEND_API_KEY no configurada — correo no enviado")
            return

        resend.api_key = api_key

        try:
            # El PDF llega ya generado en memoria, no hay archivo que leer ni borrar.
            email_attachments = [
                {
                    "filename": pdf_name,
                    "content": list(pdf_bytes),
                }
            ]

            # Add uploaded files as attachments
            if attachments:
                for file in attachments:
                    if file and hasattr(file, 'filename') and file.filename:
                        try:
                            file_content = await file.read()
                            email_attachments.append({
                                "filename": file.filename,
                                "content": list(file_content),
                            })
                            logger.info(
                                "Adjunto agregado: %d bytes", len(file_content)
                            )
                        except Exception:
                            # Sin el nombre del archivo, puede contener datos personales.
                            logger.warning(
                                "No se pudo leer un adjunto, se omite", exc_info=True
                            )

            logger.info("Enviando correo con %d adjuntos", len(email_attachments))

            resend.Emails.send(
                {
                    "from": "Portfolio <contacto@mmgonnar.com>",
                    "to": "mm.gonnar+portafolio@gmail.com",
                    "subject": f"[Brief] {brief.projectName or 'Project'} — {brief.name}",
                    "html": BriefService._build_email_html(brief),
                    "attachments": email_attachments,
                }
            )

            logger.info("Correo del brief enviado correctamente")

        except Exception:
            logger.exception("Error enviando el correo del brief")
            raise

    @staticmethod
    def _build_email_html(brief: BriefSubmission) -> str:
        features_list = "".join(f"<li>{f}</li>" for f in (brief.features or []))
        
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a1a;">📋 Nuevo Brief Recibido</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Cliente</td>
                    <td style="padding: 8px;">{brief.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">Email</td>
                    <td style="padding: 8px;">{brief.email}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Proyecto</td>
                    <td style="padding: 8px;">{brief.projectName}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">Tipo</td>
                    <td style="padding: 8px;">{brief.projectType}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Presupuesto</td>
                    <td style="padding: 8px;">{brief.budget}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">Timeline</td>
                    <td style="padding: 8px;">{brief.timeline}</td>
                </tr>
            </table>
            <h3 style="color: #1a1a1a; margin-top: 20px;">Funcionalidades requeridas</h3>
            <ul style="color: #444;">
                {features_list or '<li>No especificadas</li>'}
            </ul>
            <p style="color: #888; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">
                El brief completo está adjunto en PDF junto con los archivos subidos.
            </p>
        </div>
        """