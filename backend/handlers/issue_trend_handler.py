from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from handlers.base import WidgetDataHandler
from models import Issue, Member, Department, Project
from schemas import WidgetQueryRequest, WidgetDataResponse, SeriesData, SeriesPoint, ResultMeta

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class IssueTrendHandler(WidgetDataHandler):
    @property
    def source_key(self) -> str:
        return "issue_created_resolved_trend"

    def query(self, request: WidgetQueryRequest, db: Session) -> WidgetDataResponse:
        f = request.filters
        year          = (f.year if f else None) or datetime.now().year
        department_id = f.departmentId if f else None

        project = db.query(Project).filter(Project.key == request.projectKey).first()
        if not project:
            raise ValueError(f"Project '{request.projectKey}' not found")

        def monthly_counts(date_col, extra_filter=None):
            q = (
                db.query(
                    func.strftime("%m", date_col).label("month"),
                    func.count().label("cnt"),
                )
                .join(Issue.assignee)
                .join(Member.department)
                .filter(
                    Issue.project_id == project.id,
                    func.strftime("%Y", date_col) == str(year),
                )
            )
            if extra_filter is not None:
                q = q.filter(extra_filter)
            if department_id:
                q = q.filter(Department.id == department_id)
            return {int(r.month): r.cnt for r in q.group_by(func.strftime("%m", date_col)).all()}

        created_rows  = monthly_counts(Issue.created_at)
        resolved_rows = monthly_counts(Issue.resolved_at, Issue.resolved_at.isnot(None))

        # Build cumulative series
        c_cum = r_cum = 0
        c_data, r_data = [], []
        for m in range(1, 13):
            c_cum += created_rows.get(m, 0)
            r_cum += resolved_rows.get(m, 0)
            c_data.append(SeriesPoint(x=MONTHS[m - 1], y=c_cum))
            r_data.append(SeriesPoint(x=MONTHS[m - 1], y=r_cum))

        return WidgetDataResponse(
            dataSource=self.source_key,
            type="line_chart",
            series=[
                SeriesData(name="Created",  data=c_data),
                SeriesData(name="Resolved", data=r_data),
            ],
            meta=ResultMeta(computedAt=datetime.utcnow().isoformat(), fromCache=False, totalRows=12),
        )
