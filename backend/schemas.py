from typing import Any, Optional
from pydantic import BaseModel


# ── Project ──────────────────────────────────────────────
class ProjectOut(BaseModel):
    id: int
    key: str
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Department ───────────────────────────────────────────
class DepartmentOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ── Widget definition (inside page layout) ───────────────
class WidgetPosition(BaseModel):
    row: int
    col: int
    w: int
    h: int


class WidgetDefinition(BaseModel):
    widgetId: str
    type: str
    title: str
    dataSource: str
    position: WidgetPosition
    displayConfig: Optional[dict[str, Any]] = None
    queryConfig: Optional[dict[str, Any]] = None


# ── Page ─────────────────────────────────────────────────
class PageSummaryOut(BaseModel):
    pageId: str
    title: str
    icon: Optional[str] = None
    sortOrder: int


class PageDetailOut(BaseModel):
    pageId: str
    title: str
    icon: Optional[str] = None
    availableFilters: list[str]
    defaultFilters: dict[str, Any]
    layout: list[WidgetDefinition]


# ── Widget Data Query ─────────────────────────────────────
class DateRangeFilter(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    preset: Optional[str] = None


class WidgetFilters(BaseModel):
    year: Optional[int] = None
    departmentId: Optional[int] = None
    dateRange: Optional[DateRangeFilter] = None


class WidgetQueryRequest(BaseModel):
    projectKey: str
    pageId: str
    widgetId: str
    dataSource: str
    filters: Optional[WidgetFilters] = None


# ── Widget Data Response ──────────────────────────────────
class ResultMeta(BaseModel):
    computedAt: str
    fromCache: bool
    totalRows: int


class SeriesPoint(BaseModel):
    x: str
    y: int


class SeriesData(BaseModel):
    name: str
    data: list[SeriesPoint]


class ColumnDef(BaseModel):
    key: str
    label: str
    type: str = "string"


class WidgetDataResponse(BaseModel):
    widgetId: str
    type: str
    dataSource: str
    # line_chart / bar_chart fields
    series: Optional[list[SeriesData]] = None
    # table fields
    columns: Optional[list[ColumnDef]] = None
    rows: Optional[list[dict[str, Any]]] = None
    meta: ResultMeta
