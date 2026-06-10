from app.db.supabase_client import supabase


class ProjectData:
    @staticmethod
    def get_all():
        response = (
            supabase.table("projects")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
