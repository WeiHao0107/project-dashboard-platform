from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from handlers.base import WidgetDataHandler
from models import Issue, Member, Department, Project
from schemas import WidgetQueryRequest, WidgetDataResponse, ColumnDef, ResultMeta

MONTH_KEYS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


class MemberMonthlySummaryHandler(WidgetDataHandler):
    @property
    def source_key(self) -> str:
        return "member_monthly_summary"

    def query(self, request: WidgetQueryRequest, db: Session) -> WidgetDataResponse:
        f = request.filters
        year          = (f.year if f else None) or datetime.now().year
        department_id = f.departmentId if f else None

        project = db.query(Project).filter(Project.key == request.projectKey).first()
        if not project:
            raise ValueError(f"Project '{request.projectKey}' not found")

        q = (
            db.query(
                Member.id.label("mid"),
                Member.name.label("mname"),
                Department.name.label("dname"),
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

        pivot: dict[int, dict] = {}
        meta_map: dict[int, tuple] = {}

        for r in q.group_by(Member.id, func.strftime("%m", Issue.resolved_at)).order_by(Member.name).all():
            if r.mid not in meta_map:
                meta_map[r.mid] = (r.mname, r.dname)
            pivot.setdefault(r.mid, {})[MONTH_KEYS[int(r.month) - 1]] = r.cnt

        # Ensure all dept members appear even with 0 issues
        if not pivot:
            mq = db.query(Member).join(Member.department).filter(Department.project_id == project.id)
            if department_id:
                mq = mq.filter(Department.id == department_id)
            for m in mq.all():
                meta_map.setdefault(m.id, (m.name, m.department.name))
                pivot.setdefault(m.id, {})

        rows = []
        for mid, monthly in sorted(pivot.items(), key=lambda x: meta_map[x[0]][0]):
            name, dept = meta_map[mid]
            row = {"member": name, "department": dept}
            total = 0
            for mk in MONTH_KEYS:
                v = monthly.get(mk, 0)
                row[mk] = v
                total += v
            row["total"] = total
            rows.append(row)

        columns = (
            [ColumnDef(key="member", label="Member", type="string"),
             ColumnDef(key="department", label="Department", type="string")]
            + [ColumnDef(key=mk, label=mk, type="number") for mk in MONTH_KEYS]
            + [ColumnDef(key="total", label="Total", type="number")]
        )

        return WidgetDataResponse(
            dataSource=self.source_key,
            type="table",
            columns=columns,
            rows=rows,
            meta=ResultMeta(computedAt=datetime.utcnow().isoformat(), fromCache=False, totalRows=len(rows)),
        )
