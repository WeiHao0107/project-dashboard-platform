"""
Seed script – run once: python seed.py
"""
import random
from datetime import datetime, timedelta

from database import engine, SessionLocal, Base
from models import (
    Project, Department, Member, Issue,
    CustomPage, WidgetDataSourceRegistry,
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

MONTHLY_WEIGHTS = [0.8, 0.7, 1.0, 1.1, 1.2, 1.0, 0.9, 0.8, 1.1, 1.2, 1.1, 0.7]


# ── page list (simple — no layout config) ────────────────

PAGES = [
    {"page_key": "issue-trend",        "page_name": "Issue Trend",        "icon": "chart-line", "sort_order": 0},
    {"page_key": "member-performance", "page_name": "Member Performance", "icon": "users",      "sort_order": 1},
]


# ── data source registry ──────────────────────────────────

DATA_SOURCES = [
    {
        "source_key": "issue_created_resolved_trend",
        "source_name": "Issue Created vs Resolved Trend",
        "description": "Cumulative monthly created and resolved issue counts",
        "backend_handler": "IssueTrendHandler",
        "supported_filters": ["year", "departmentId"],
    },
    {
        "source_key": "member_monthly_summary",
        "source_name": "Member Monthly Issue Summary",
        "description": "Issues resolved per member per month",
        "backend_handler": "MemberMonthlySummaryHandler",
        "supported_filters": ["year", "departmentId"],
    },
]


# ── project / department / member data ───────────────────

PROJECTS_DATA = [
    {
        "key": "PLATFORM",
        "name": "Platform Team",
        "description": "Core platform infrastructure and services",
        "departments": [
            {"name": "Backend",  "members": ["Alice Chen", "Bob Wang", "Carol Liu", "David Zhang"]},
            {"name": "Frontend", "members": ["Eve Lin", "Frank Huang", "Grace Wu"]},
            {"name": "DevOps",   "members": ["Henry Chou", "Iris Tsai"]},
        ],
    },
    {
        "key": "MOBILE",
        "name": "Mobile App",
        "description": "iOS and Android mobile application",
        "departments": [
            {"name": "iOS",     "members": ["Jack Lee", "Kate Chen", "Leo Yang"]},
            {"name": "Android", "members": ["Mia Wang", "Nathan Liu", "Olivia Ho"]},
            {"name": "QA",      "members": ["Paul Cheng", "Quinn Xu"]},
        ],
    },
    {
        "key": "ANALYTICS",
        "name": "Data Analytics",
        "description": "Data pipeline and analytics platform",
        "departments": [
            {"name": "Data Engineering", "members": ["Rachel Sun", "Sam Liao", "Tina Kuo", "Uma Chen"]},
            {"name": "Data Science",     "members": ["Victor Hsu", "Wendy Pan", "Xavier Luo"]},
        ],
    },
]


def generate_issues(project: Project, members: list[Member], year: int, base_count: int):
    issues, counter = [], 1
    for month_idx in range(12):
        month = month_idx + 1
        n = max(1, int(base_count * MONTHLY_WEIGHTS[month_idx] + random.randint(-3, 3)))
        m_start = datetime(year, month, 1)
        m_end   = datetime(year, 12, 31, 23, 59, 59) if month == 12 \
                  else datetime(year, month + 1, 1) - timedelta(seconds=1)
        for _ in range(n):
            created  = random_date(m_start, m_end)
            assignee = random.choice(members) if members else None
            status   = random.choices(
                ["open", "in_progress", "done", "closed"],
                weights=[5, 10, 60, 25],
            )[0]
            resolved_at = None
            if status in ("done", "closed"):
                resolved_at = created + timedelta(days=random.randint(1, 25))
                if resolved_at > m_end + timedelta(days=30):
                    resolved_at = m_end + timedelta(days=30)
            issues.append(Issue(
                project_id=project.id,
                assignee_id=assignee.id if assignee else None,
                issue_key=f"{project.key}-{counter}",
                title=random.choice(ISSUE_TITLES),
                status=status,
                priority=random.choice(["low", "medium", "high", "critical"]),
                created_at=created,
                resolved_at=resolved_at,
            ))
            counter += 1
    return issues


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    for ds in DATA_SOURCES:
        db.add(WidgetDataSourceRegistry(**ds))
    db.flush()

    for proj_data in PROJECTS_DATA:
        project = Project(key=proj_data["key"], name=proj_data["name"], description=proj_data["description"])
        db.add(project)
        db.flush()

        all_members = []
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

        for page_data in PAGES:
            db.add(CustomPage(project_id=project.id, **page_data))

        base = {"PLATFORM": 18, "MOBILE": 15, "ANALYTICS": 12}[proj_data["key"]]
        for year in [2024, 2025, 2026]:
            for iss in generate_issues(project, all_members, year, base):
                db.add(iss)

    db.commit()
    db.close()
    print("✅ Seed completed.")


if __name__ == "__main__":
    seed()
