"""
Seed script – generates fake data for the dashboard platform.
Run once: python seed.py
"""
import random
from datetime import datetime, timedelta

from database import engine, SessionLocal, Base
from models import (
    Project, Department, Member, Issue,
    CustomPageDefinition, WidgetDataSourceRegistry,
)

random.seed(42)

# ── helpers ──────────────────────────────────────────────

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


ISSUE_TITLES = [
    "Fix login redirect bug", "Add export to CSV feature", "Improve search performance",
    "Update API documentation", "Refactor auth middleware", "Mobile layout broken on iOS",
    "Database query optimization", "Add unit tests for payment flow", "Deploy to staging env",
    "Fix null pointer exception", "Add dark mode support", "Integrate Slack notifications",
    "Implement rate limiting", "Fix memory leak in worker", "Add pagination to list API",
    "UI component library upgrade", "Fix CORS configuration", "Improve error messages",
    "Add email verification flow", "Performance profiling report", "Fix timezone handling",
    "Add retry logic for webhooks", "Database migration script", "Fix XSS vulnerability",
    "Improve onboarding UX", "Add audit log", "Optimize image uploads",
    "Fix cache invalidation bug", "Add API versioning", "Improve test coverage",
]

STATUSES = ["open", "in_progress", "done", "closed"]
PRIORITIES = ["low", "medium", "high", "critical"]


# ── page definitions ─────────────────────────────────────

PAGES = [
    {
        "page_key": "issue-trend",
        "page_name": "Issue Trend",
        "description": "Created vs Resolved issues over time",
        "icon": "chart-line",
        "available_filters": ["year", "department"],
        "default_filters": {"year": 2025},
        "sort_order": 0,
        "layout_config": [
            {
                "widgetId": "trend-chart",
                "type": "line_chart",
                "title": "Created vs Resolved Issues (Cumulative)",
                "dataSource": "issue_created_resolved_trend",
                "position": {"row": 0, "col": 0, "w": 12, "h": 5},
                "displayConfig": {
                    "colors": ["#5470c6", "#91cc75"],
                    "xAxisLabel": "Month",
                    "yAxisLabel": "Cumulative Count",
                    "showLegend": True,
                },
            }
        ],
    },
    {
        "page_key": "member-performance",
        "page_name": "Member Performance",
        "description": "Monthly issue count per team member",
        "icon": "users",
        "available_filters": ["year", "department"],
        "default_filters": {"year": 2025},
        "sort_order": 1,
        "layout_config": [
            {
                "widgetId": "member-table",
                "type": "table",
                "title": "Issues Handled Per Member (Monthly)",
                "dataSource": "member_monthly_summary",
                "position": {"row": 0, "col": 0, "w": 12, "h": 8},
                "displayConfig": {
                    "sortBy": "total",
                    "sortOrder": "desc",
                },
            }
        ],
    },
]

# ── data source registry ──────────────────────────────────

DATA_SOURCES = [
    {
        "source_key": "issue_created_resolved_trend",
        "source_name": "Issue Created vs Resolved Trend",
        "description": "Monthly created and resolved issue counts",
        "backend_handler": "IssueTrendHandler",
        "supported_filters": ["year", "departmentId"],
        "output_schema": {"type": "timeseries", "series": ["created", "resolved"]},
    },
    {
        "source_key": "member_monthly_summary",
        "source_name": "Member Monthly Issue Summary",
        "description": "Issues resolved per member per month",
        "backend_handler": "MemberMonthlySummaryHandler",
        "supported_filters": ["year", "departmentId"],
        "output_schema": {"type": "pivot_table", "dimensions": ["member", "month"]},
    },
]

# ── project / department / member data ───────────────────

PROJECTS_DATA = [
    {
        "key": "PLATFORM",
        "name": "Platform Team",
        "description": "Core platform infrastructure and services",
        "departments": [
            {
                "name": "Backend",
                "members": ["Alice Chen", "Bob Wang", "Carol Liu", "David Zhang"],
            },
            {
                "name": "Frontend",
                "members": ["Eve Lin", "Frank Huang", "Grace Wu"],
            },
            {
                "name": "DevOps",
                "members": ["Henry Chou", "Iris Tsai"],
            },
        ],
    },
    {
        "key": "MOBILE",
        "name": "Mobile App",
        "description": "iOS and Android mobile application",
        "departments": [
            {
                "name": "iOS",
                "members": ["Jack Lee", "Kate Chen", "Leo Yang"],
            },
            {
                "name": "Android",
                "members": ["Mia Wang", "Nathan Liu", "Olivia Ho"],
            },
            {
                "name": "QA",
                "members": ["Paul Cheng", "Quinn Xu"],
            },
        ],
    },
    {
        "key": "ANALYTICS",
        "name": "Data Analytics",
        "description": "Data pipeline and analytics platform",
        "departments": [
            {
                "name": "Data Engineering",
                "members": ["Rachel Sun", "Sam Liao", "Tina Kuo", "Uma Chen"],
            },
            {
                "name": "Data Science",
                "members": ["Victor Hsu", "Wendy Pan", "Xavier Luo"],
            },
        ],
    },
]


# ── monthly creation weight (makes trend more realistic) ──
# index 0 = Jan ... 11 = Dec
MONTHLY_WEIGHTS = [0.8, 0.7, 1.0, 1.1, 1.2, 1.0, 0.9, 0.8, 1.1, 1.2, 1.1, 0.7]


def generate_issues(project: Project, members: list[Member], year: int, base_count: int):
    issues = []
    issue_counter = 1

    for month_idx in range(12):
        month = month_idx + 1
        n = max(1, int(base_count * MONTHLY_WEIGHTS[month_idx] + random.randint(-3, 3)))
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year, 12, 31, 23, 59, 59)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)

        for _ in range(n):
            created = random_date(month_start, month_end)
            assignee = random.choice(members) if members else None

            # ~85% resolved
            resolved_at = None
            status = random.choices(
                ["open", "in_progress", "done", "closed"],
                weights=[5, 10, 60, 25],
            )[0]
            if status in ("done", "closed"):
                days_to_resolve = random.randint(1, 25)
                resolved_at = created + timedelta(days=days_to_resolve)
                # ensure resolved date doesn't exceed end of next month
                max_resolve = month_end + timedelta(days=30)
                if resolved_at > max_resolve:
                    resolved_at = max_resolve

            issues.append(
                Issue(
                    project_id=project.id,
                    assignee_id=assignee.id if assignee else None,
                    issue_key=f"{project.key}-{issue_counter}",
                    title=random.choice(ISSUE_TITLES),
                    status=status,
                    priority=random.choice(PRIORITIES),
                    created_at=created,
                    resolved_at=resolved_at,
                )
            )
            issue_counter += 1

    return issues


# ── main ─────────────────────────────────────────────────

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # data sources
    for ds in DATA_SOURCES:
        db.add(WidgetDataSourceRegistry(**ds))
    db.flush()

    all_members_by_project: dict[str, list[Member]] = {}

    for proj_data in PROJECTS_DATA:
        project = Project(
            key=proj_data["key"],
            name=proj_data["name"],
            description=proj_data["description"],
        )
        db.add(project)
        db.flush()

        all_members: list[Member] = []

        for dept_data in proj_data["departments"]:
            dept = Department(project_id=project.id, name=dept_data["name"])
            db.add(dept)
            db.flush()

            for mname in dept_data["members"]:
                m = Member(
                    department_id=dept.id,
                    name=mname,
                    email=mname.lower().replace(" ", ".") + "@example.com",
                )
                db.add(m)
                db.flush()
                all_members.append(m)

        all_members_by_project[proj_data["key"]] = all_members

        # pages
        for page_data in PAGES:
            page = CustomPageDefinition(
                project_id=project.id,
                page_key=page_data["page_key"],
                page_name=page_data["page_name"],
                description=page_data["description"],
                icon=page_data["icon"],
                layout_config=page_data["layout_config"],
                default_filters=page_data["default_filters"],
                available_filters=page_data["available_filters"],
                sort_order=page_data["sort_order"],
            )
            db.add(page)

        # issues – 2024 and 2025
        base = {"PLATFORM": 18, "MOBILE": 15, "ANALYTICS": 12}[proj_data["key"]]
        for year in [2024, 2025]:
            issues = generate_issues(project, all_members, year, base)
            for iss in issues:
                db.add(iss)

    db.commit()
    db.close()

    print("✅ Seed completed.")
    for key, members in all_members_by_project.items():
        print(f"  {key}: {len(members)} members")


if __name__ == "__main__":
    seed()
