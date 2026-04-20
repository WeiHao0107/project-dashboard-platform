from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from handlers.registry import get_handler
from schemas import WidgetQueryRequest, WidgetDataResponse

router = APIRouter(prefix="/api/widget-data", tags=["widget-data"])


@router.post("/query", response_model=WidgetDataResponse)
def query_widget(request: WidgetQueryRequest, db: Session = Depends(get_db)):
    try:
        handler = get_handler(request.dataSource)
        return handler.query(request, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {e}")
