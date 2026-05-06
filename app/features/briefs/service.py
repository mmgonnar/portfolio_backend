import os
import resend  # type: ignore[import-not-found]
import logging

from typing import List, Optional
from fastapi import UploadFile
from app.models.brief import BriefSubmission
from app.utils.pdf_generator import generate_brief_pdf

logger = logging.getLogger(__name__)


class BriefService:

    @staticmethod
    async def submit_brief(brief: BriefSubmission, attachments: List[UploadFile] = None) -> dict:
        print(f"📧 submit_brief called - projectName: {brief.projectName}")
        data = brief.model_dump()
        print(f"📧 Brief data: {list(data.keys())}")
        
        pdf_path = generate_brief_pdf(data)
        logger.info(f"PDF generado: {pdf_path}")
        print(f"📧 PDF generated: {pdf_path}")

        print(f"📧 Sending email with attachments: {attachments}")
        await BriefService._send_email(brief, pdf_path, attachments)

        return {
            "status": "success",
            "message": "Brief recibido. Te contactaré pronto.",
            "pdf_path": pdf_path,
        }

    @staticmethod
    async def _send_email(brief: BriefSubmission, pdf_path: str, attachments: List[UploadFile] = None) -> None:
        api_key = os.environ.get("RESEND_API_KEY")

        if not api_key:
            logger.warning("RESEND_API_KEY no configurada — correo no enviado")
            return

        resend.api_key = api_key

        try:
            # Read PDF
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            pdf_attachment_name = f"Brief_{brief.projectName or brief.name or 'Project'}.pdf"

            # Build attachments list with PDF
            email_attachments = [
                {
                    "filename": pdf_attachment_name,
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
                            print(f"📎 Attached: {file.filename} ({len(file_content)} bytes)")
                        except Exception as file_err:
                            print(f"⚠️ File read error: {file_err}")

            print(f"📎 Sending email with {len(email_attachments)} attachment(s)")

            resend.Emails.send(
                {
                    "from": "Portfolio <contacto@mmgonnar.com>",
                    "to": "mm.gonnar+portafolio@gmail.com",
                    "subject": f"[Brief] {brief.projectName or 'Project'} — {brief.name}",
                    "html": BriefService._build_email_html(brief),
                    "attachments": email_attachments,
                }
            )

            logger.info(f"Correo enviado: {brief.projectName}")
            print("✅ Correo enviado correctamente")

        except Exception as e:
            logger.error(f"Error enviando correo: {str(e)}")
            print(f"ERROR RESEND: {str(e)}")
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