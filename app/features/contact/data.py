from app.db.supabase_client import supabase
from app.models.schemas import ContactMessage

class ContactData:
    @staticmethod
    def save(message: ContactMessage):
        data_to_save = message.model_dump()
        
        if "phone_extension" in data_to_save:
            del data_to_save["phone_extension"]
            
        response = supabase.table("portfolio_contact").insert(data_to_save).execute()
        
        return response.data