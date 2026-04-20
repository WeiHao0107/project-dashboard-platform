from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Project, CustomPage
from schemas import PageOut

router = APIRouter(prefix="/api/projects", tags=["pages"])


@router.get("/{project_key}/pages", response_model=list[PageOut])
def list_pages(project_key: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.key == project_key).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pages = (
        db.query(CustomPage)
        .filter(CustomPage.project_id == project.id, CustomPage.is_active == True)
        .order_by(CustomPage.sort_order)
        .all()
    )
    return [
        PageOut(pageId=p.page_key, title=p.page_name, icon=p.icon, sortOrder=p.sort_order)
        for p in pages
    ]
