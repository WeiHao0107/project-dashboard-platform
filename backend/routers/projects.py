from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Project, Department
from schemas import ProjectOut, DepartmentOut

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.name).all()


@router.get("/{project_key}/departments", response_model=list[DepartmentOut])
def list_departments(project_key: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.key == project_key).first()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    return (
        db.query(Department)
        .filter(Department.project_id == project.id)
        .order_by(Department.name)
        .all()
    )
