import os
import resend  # type: ignore[import-not-found]
import logging

from app.models.brief import BriefSubmission
from app.utils.pdf_generator import generate_brief_pdf

logger = logging.getLogger(__name__)


class BriefService:

    @staticmethod
    def submit_brief(brief: BriefSubmission) -> dict:
        data = brief.model_dump()
        pdf_path = generate_brief_pdf(data)
        logger.info(f"PDF generado: {pdf_path}")

        BriefService._send_email(brief, pdf_path)

        return {
            "status": "success",
            "message": "Brief recibido. Te contactaré pronto.",
            "pdf_path": pdf_path,
        }

    @staticmethod
    def _send_email(brief: BriefSubmission, pdf_path: str) -> None:
        api_key = os.environ.get("RESEND_API_KEY")

        if not api_key:
            logger.warning("RESEND_API_KEY no configurada — correo no enviado")
            return

        resend.api_key = api_key

        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            attachment_name = f"Brief_{brief.projectName}.pdf"

            print(f"PDF path: {pdf_path}")
            print(f"PDF size: {len(pdf_bytes)} bytes")
            print(f"Attachment name: {attachment_name}")

            resend.Emails.send(
                {
                    "from": "Portfolio <contacto@mmgonnar.com>",
                    "to": "mm.gonnar+portafolio@gmail.com",
                    "subject": f"[Brief] {brief.projectName} — {brief.name}",
                    "html": BriefService._build_email_html(brief),
                    "attachments": [
                        {
                            "filename": attachment_name,
                            "content": list(pdf_bytes),
                        }
                    ],
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
        features_list = "".join(f"<li>{f}</li>" for f in brief.features)

        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #1a1a1a;">📋 Nuevo Brief Recibido</h2>

            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; font-weight: bold; color: #555; width: 40%;">Cliente</td>
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
                    <td style="padding: 8px;">{brief.projectType.value}</td>
                </tr>
                <tr style="background: #f9f9f9;">
                    <td style="padding: 8px; font-weight: bold; color: #555;">Presupuesto</td>
                    <td style="padding: 8px;">{brief.budget.value}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; font-weight: bold; color: #555;">Timeline</td>
                    <td style="padding: 8px;">{brief.timeline.value}</td>
                </tr>
            </table>

            <h3 style="color: #1a1a1a; margin-top: 20px;">Funcionalidades requeridas</h3>
            <ul style="color: #444;">
                {features_list}
            </ul>

            <p style="color: #888; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 10px;">
                El brief completo está adjunto en PDF.
            </p>
        </div>
        """