import http
from app.features.projects.data import ProjectData
from fastapi import HTTPException

class ProjectService:
    @staticmethod
    def list_projects():
        try:
            data = ProjectData.get_all()
            print(f"PROYECTOS DESDE SUPA: {data}")
            return data
            # return ProjectData.get_all()
        except Exception as e:
            print(f"Error loading projects: {e}")
            raise HTTPException(status_code=500, detail="Error getting projects")