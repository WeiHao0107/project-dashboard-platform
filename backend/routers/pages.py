from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Project, CustomPageDefinition
from schemas import PageSummaryOut, PageDetailOut, WidgetDefinition, WidgetPosition

router = APIRouter(prefix="/api/projects", tags=["pages"])


def _to_detail(page: CustomPageDefinition) -> PageDetailOut:
    widgets = []
    for w in (page.layout_config or []):
        pos = w.get("position", {})
        widgets.append(
            WidgetDefinition(
                widgetId=w["widgetId"],
                type=w["type"],
                title=w["title"],
                dataSource=w["dataSource"],
                position=WidgetPosition(**pos),
                displayConfig=w.get("displayConfig"),
                queryConfig=w.get("queryConfig"),
            )
        )
    return PageDetailOut(
        pageId=page.page_key,
        title=page.page_name,
        icon=page.icon,
        availableFilters=page.available_filters or [],
        defaultFilters=page.default_filters or {},
        layout=widgets,
    )


@router.get("/{project_key}/pages", response_model=list[PageSummaryOut])
def list_pages(project_key: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.key == project_key).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    pages = (
        db.query(CustomPageDefinition)
        .filter(
            CustomPageDefinition.project_id == project.id,
            CustomPageDefinition.is_active == True,
        )
        .order_by(CustomPageDefinition.sort_order)
        .all()
    )
    return [
        PageSummaryOut(
            pageId=p.page_key,
            title=p.page_name,
            icon=p.icon,
            sortOrder=p.sort_order,
        )
        for p in pages
    ]


@router.get("/{project_key}/pages/{page_id}", response_model=PageDetailOut)
def get_page(project_key: str, page_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.key == project_key).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    page = (
        db.query(CustomPageDefinition)
        .filter(
            CustomPageDefinition.project_id == project.id,
            CustomPageDefinition.page_key == page_id,
            CustomPageDefinition.is_active == True,
        )
        .first()
    )
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return _to_detail(page)
