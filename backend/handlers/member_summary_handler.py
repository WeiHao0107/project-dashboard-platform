from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from handlers.base import WidgetDataHandler
from models import Issue, Member, Department, Project
from schemas import (
    WidgetQueryRequest, WidgetDataResponse,
    ColumnDef, ResultMeta,
)

MONTH_KEYS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class MemberMonthlySummaryHandler(WidgetDataHandler):
    @property
    def source_key(self) -> str:
        return "member_monthly_summary"

    def query(self, request: WidgetQueryRequest, db: Session) -> WidgetDataResponse:
        filters = request.filters or {}
        year = getattr(filters, "year", None) or datetime.now().year
        department_id = getattr(filters, "departmentId", None)

        project = db.query(Project).filter(Project.key == request.projectKey).first()
        if not project:
            raise ValueError(f"Project '{request.projectKey}' not found")

        # Query: issues resolved per member per month
        q = (
            db.query(
                Member.id.label("member_id"),
                Member.name.label("member_name"),
                Department.name.label("dept_name"),
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
            q = q.filter(Department.id == department_id)

        rows_raw = q.group_by(
            Member.id, func.strftime("%m", Issue.resolved_at)
        ).order_by(Member.name).all()

        # Pivot: member → {month_key: count}
        pivot: dict[tuple, dict[str, int]] = {}
        meta_map: dict[int, tuple[str, str]] = {}  # member_id → (name, dept)

        for r in rows_raw:
            if r.member_id not in meta_map:
                meta_map[r.member_id] = (r.member_name, r.dept_name)
            key = r.member_id
            month_label = MONTH_KEYS[int(r.month) - 1]
            pivot.setdefault(key, {})[month_label] = r.cnt

        # If no resolved issues at all, still show all members in dept
        if not pivot:
            member_q = db.query(Member).join(Member.department).filter(
                Department.project_id == project.id
            )
            if department_id:
                member_q = member_q.filter(Department.id == department_id)
            for m in member_q.all():
                meta_map[m.id] = (m.name, m.department.name)
                pivot[m.id] = {}

        # Build output rows
        output_rows = []
        for mid, monthly in sorted(pivot.items(), key=lambda x: meta_map[x[0]][0]):
            name, dept = meta_map[mid]
            row: dict = {"member": name, "department": dept}
            total = 0
            for mk in MONTH_KEYS:
                v = monthly.get(mk, 0)
                row[mk] = v
                total += v
            row["total"] = total
            output_rows.append(row)

        # Columns
        columns = [
            ColumnDef(key="member", label="Member", type="string"),
            ColumnDef(key="department", label="Department", type="string"),
        ]
        for mk in MONTH_KEYS:
            columns.append(ColumnDef(key=mk, label=mk, type="number"))
        columns.append(ColumnDef(key="total", label="Total", type="number"))

        return WidgetDataResponse(
            widgetId=request.widgetId,
            type="table",
            dataSource=self.source_key,
            columns=columns,
            rows=output_rows,
            meta=ResultMeta(
                computedAt=datetime.utcnow().isoformat(),
                fromCache=False,
                totalRows=len(output_rows),
            ),
        )
