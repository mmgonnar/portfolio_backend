from app.db.supabase_client import supabase
from app.models.schemas import ContactMessage, Optional

class ContactData:
    @staticmethod
    def save(message: ContactMessage):
        response = supabase.table("portfolio_contact").insert(message.model_dump()).execute()
        return response.data

