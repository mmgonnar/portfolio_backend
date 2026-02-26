from app.features.contact.data import ContactData
from app.models.schemas import ContactMessage
from fastapi import HTTPException

class ContactService:
    @staticmethod
    def submit_contact(message: ContactMessage):
        try:
            data = ContactData.save(message)
            return {"status": "success", "data": data}
        except Exception as e:
            print(f"Error saving contact: {e}")
            raise HTTPException(status_code=500, detail="Internal error saving message")