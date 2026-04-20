from datetime import datetime
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from handlers.base import WidgetDataHandler
from models import Issue, Member, Department, Project
from schemas import (
    WidgetQueryRequest, WidgetDataResponse,
    SeriesData, SeriesPoint, ResultMeta,
)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class IssueTrendHandler(WidgetDataHandler):
    @property
    def source_key(self) -> str:
        return "issue_created_resolved_trend"

    def query(self, request: WidgetQueryRequest, db: Session) -> WidgetDataResponse:
        filters = request.filters or {}
        year = getattr(filters, "year", None) or datetime.now().year
        department_id = getattr(filters, "departmentId", None)

        project = db.query(Project).filter(Project.key == request.projectKey).first()
        if not project:
            raise ValueError(f"Project '{request.projectKey}' not found")

        # base issue query scoped to project + optional department
        def base_q(date_col):
            q = db.query(
                func.strftime("%m", date_col).label("month"),
                func.count().label("cnt"),
            ).join(Issue.assignee).join(Member.department).join(
                Project, Issue.project_id == Project.id
            ).filter(
                Issue.project_id == project.id,
                func.strftime("%Y", date_col) == str(year),
            )
            if department_id:
                q = q.filter(Department.id == department_id)
            return q.group_by(func.strftime("%m", date_col))

        # created series
        created_rows = {
            int(r.month): r.cnt
            for r in base_q(Issue.created_at).all()
        }

        # resolved series (only issues that have a resolved_at)
        resolved_q = (
            db.query(
                func.strftime("%m", Issue.resolved_at).label("month"),
                func.count().label("cnt"),
            )
            .join(Issue.assignee)
            .join(Member.department)
            .filter(
                Issue.project_id == project.id,
                Issue.resolved_at.isnot(None),
                func.strftime("%Y", Issue.resolved_at) == str(year),
            )
        )
        if department_id:
            resolved_q = resolved_q.filter(Department.id == department_id)
        resolved_rows = {
            int(r.month): r.cnt
            for r in resolved_q.group_by(func.strftime("%m", Issue.resolved_at)).all()
        }

        # Accumulate to cumulative sums
        created_cum, resolved_cum = 0, 0
        created_data, resolved_data = [], []
        for m in range(1, 13):
            created_cum  += created_rows.get(m, 0)
            resolved_cum += resolved_rows.get(m, 0)
            created_data.append(SeriesPoint(x=MONTHS[m - 1], y=created_cum))
            resolved_data.append(SeriesPoint(x=MONTHS[m - 1], y=resolved_cum))

        created_series = SeriesData(name="Created (Cumulative)", data=created_data)
        resolved_series = SeriesData(name="Resolved (Cumulative)", data=resolved_data)

        return WidgetDataResponse(
            widgetId=request.widgetId,
            type="line_chart",
            dataSource=self.source_key,
            series=[created_series, resolved_series],
            meta=ResultMeta(
                computedAt=datetime.utcnow().isoformat(),
                fromCache=False,
                totalRows=12,
            ),
        )
