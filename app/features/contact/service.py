import resend
import os
import uuid
from app.features.contact.data import ContactData
from app.models.schemas import ContactMessage
from fastapi import HTTPException

# Cargamos la API Key una sola vez
resend.api_key = os.getenv("RESEND_API_KEY")

class ContactService:
    @staticmethod
    def submit_contact(message: ContactMessage):
        # 1. Validación Honeypot
        if message.phone_extension:
            print("Bot detectado por honeypot")
            return {"status": "success", "message": "Processed"}

        # 2. Generar Identificador Único
        ticket_id = f"REF-{str(uuid.uuid4())[:8].upper()}"

        try:
            # 3. Guardar en Base de Datos (Prioridad)
            data = ContactData.save(message)

            # 4. Intentar enviar correo con Resend
            if resend.api_key:
                try:
                    resend.Emails.send({
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
                        """
                    })
                except Exception as mail_error:
                    # Si falla el mail, lo logueamos pero no detenemos el proceso
                    print(f"Error enviando correo con Resend: {mail_error}")
            else:
                print("Advertencia: RESEND_API_KEY no configurada.")

            # 5. RETORNO SIEMPRE AL FINAL DEL TRY
            return {
                "status": "success", 
                "data": data, 
                "ticket_id": ticket_id
            }
            
        except Exception as e:
            print(f"Error crítico en submit_contact: {e}")
            raise HTTPException(
                status_code=500, 
                detail="No se pudo procesar el mensaje internamente"
            )