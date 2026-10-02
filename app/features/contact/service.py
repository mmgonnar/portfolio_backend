import logging
import resend  # type: ignore[import-not-found]
import os
import uuid
from app.features.contact.data import ContactData
from app.models.schemas import ContactMessage
from fastapi import HTTPException  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

# Cargamos la API Key una sola vez
resend.api_key = os.getenv("RESEND_API_KEY")


class ContactService:
    @staticmethod
    def submit_contact(message: ContactMessage):
        if message.phone_extension:
            logger.info("Contacto descartado por honeypot")
            return {"status": "success", "message": "Processed"}

        ticket_id = f"REF-{str(uuid.uuid4())[:8].upper()}"

        try:
            data = ContactData.save(message)

            if resend.api_key:
                try:
                    resend.Emails.send(
                        {
                            "from": "Portfolio <contacto@mmgonnar.com>",
                            "to": "mm.gonnar+portafolio@gmail.com",
                            "subject": f"[{ticket_id}] Nuevo mensaje de {message.name}",
                            "html": f"""
                            <h3>Nuevo contacto desde mmgonnar.com</h3>
                            <p><strong>De:</strong> {message.name} ({message.email})</p>
                            <p><strong>Referencia:</strong> {ticket_id}</p>
                            <hr />
                            <p><strong>Mensaje:</strong></p>
                            <p style="white-space: pre-wrap;">{message.message}</p>
                            <hr />
                            <small>Este mensaje fue guardado en la base de datos con éxito.</small>
                        """,
                        }
                    )
                except Exception:
                    logger.exception("Error enviando el correo de contacto")
            else:
                logger.warning("RESEND_API_KEY no configurada, correo no enviado")

            return {"status": "success", "data": data, "ticket_id": ticket_id}

        except Exception:
            logger.exception("Error critico en submit_contact")
            raise HTTPException(
                status_code=500,
                detail="No se pudo procesar el mensaje internamente. Por favor intente mas tarde",
            )
