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


# ── Page (simple list item) ───────────────────────────────
class PageOut(BaseModel):
    pageId:    str
    title:     str
    icon:      Optional[str] = None
    sortOrder: int


# ── Widget Data Query ─────────────────────────────────────
class WidgetFilters(BaseModel):
    year:         Optional[int] = None
    departmentId: Optional[int] = None


class WidgetQueryRequest(BaseModel):
    projectKey: str
    dataSource: str
    filters:    Optional[WidgetFilters] = None


# ── Widget Data Response ──────────────────────────────────
class ResultMeta(BaseModel):
    computedAt: str
    fromCache:  bool
    totalRows:  int


class SeriesPoint(BaseModel):
    x: str
    y: int


class SeriesData(BaseModel):
    name: str
    data: list[SeriesPoint]


class ColumnDef(BaseModel):
    key:   str
    label: str
    type:  str = "string"


class WidgetDataResponse(BaseModel):
    dataSource: str
    type:       str
    series:  Optional[list[SeriesData]]        = None
    columns: Optional[list[ColumnDef]]         = None
    rows:    Optional[list[dict[str, Any]]]    = None
    meta:    ResultMeta
