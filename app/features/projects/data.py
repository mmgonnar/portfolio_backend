from app.db.supabase_client import supabase

class ProjectData:
    @staticmethod
    def get_all():
        response = supabase.table("portfolio_projects").select("*").order("id", desc=True).execute()
        return response.data
