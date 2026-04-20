from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from database import Base


class Project(Base):
    __tablename__ = "projects"

    id         = Column(Integer, primary_key=True, index=True)
    key        = Column(String(50), unique=True, nullable=False, index=True)
    name       = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    departments = relationship("Department", back_populates="project")
    issues      = relationship("Issue", back_populates="project")
    pages       = relationship("CustomPageDefinition", back_populates="project")


class Department(Base):
    __tablename__ = "departments"

    id         = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name       = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="departments")
    members = relationship("Member", back_populates="department")


class Member(Base):
    __tablename__ = "members"

    id            = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name          = Column(String(255), nullable=False)
    email         = Column(String(255))
    created_at    = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="members")
    issues     = relationship("Issue", back_populates="assignee")


class Issue(Base):
    __tablename__ = "issues"

    id          = Column(Integer, primary_key=True, index=True)
    project_id  = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    issue_key   = Column(String(50), nullable=False, index=True)
    title       = Column(String(500), nullable=False)
    status      = Column(String(50), nullable=False, default="open")
    priority    = Column(String(20), default="medium")
    created_at  = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    project  = relationship("Project", back_populates="issues")
    assignee = relationship("Member", back_populates="issues")


class CustomPageDefinition(Base):
    __tablename__ = "custom_page_definitions"

    id               = Column(Integer, primary_key=True, index=True)
    project_id       = Column(Integer, ForeignKey("projects.id"), nullable=False)
    page_key         = Column(String(100), nullable=False)
    page_name        = Column(String(255), nullable=False)
    description      = Column(Text)
    icon             = Column(String(50))
    layout_config    = Column(JSON, nullable=False, default=list)
    default_filters  = Column(JSON, nullable=False, default=dict)
    available_filters = Column(JSON, nullable=False, default=list)
    is_active        = Column(Boolean, default=True)
    sort_order       = Column(Integer, default=0)
    created_at       = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="pages")


class WidgetDataSourceRegistry(Base):
    __tablename__ = "widget_data_source_registry"

    id               = Column(Integer, primary_key=True, index=True)
    source_key       = Column(String(100), unique=True, nullable=False)
    source_name      = Column(String(255), nullable=False)
    description      = Column(Text)
    backend_handler  = Column(String(255), nullable=False)
    supported_filters = Column(JSON, default=list)
    output_schema    = Column(JSON, default=dict)
    is_active        = Column(Boolean, default=True)
