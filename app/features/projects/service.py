from app.features.projects.data import ProjectData
from app.models.schemas import ProjectResponse
from fastapi import HTTPException


class ProjectService:
    @staticmethod
    def list_projects(lang: str = "es"):
        try:
            raw = ProjectData.get_all()
            projects = []
            for item in raw:
                projects.append(
                    ProjectResponse(
                        id=item["id"],
                        title=item[f"title_{lang}"],
                        description=item[f"description_{lang}"],
                        architecture=item[f"architecture_{lang}"],
                        technical_details=item[f"technical_details_{lang}"],
                        image_url=item["image_url"],
                        logo_url=item.get("logo_url"),
                        repository_url=item.get("repository_url"),
                        live_url=item.get("live_url"),
                        technologies=item["technologies"],
                        created_at=item["created_at"],
                    )
                )
            return projects
        except Exception as e:
            print(f"Error loading projects: {e}")
            raise HTTPException(status_code=500, detail="Error getting projects")