from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Project(Base):
    __tablename__ = "project"

    project_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)


class OccurrencePhase(Base):
    __tablename__ = "occurrence_phase"

    phase_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase_name: Mapped[str] = mapped_column(String(50), nullable=False)


class Location(Base):
    __tablename__ = "location"

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    location_name: Mapped[str] = mapped_column(String(100), nullable=False)


class ResponsibleDept(Base):
    __tablename__ = "responsible_dept"

    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_name: Mapped[str] = mapped_column(String(100), nullable=False)


class TechDept(Base):
    __tablename__ = "tech_dept"

    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_name: Mapped[str] = mapped_column(String(100), nullable=False)


class ProductionTechOwner(Base):
    __tablename__ = "production_tech_owner"

    owner_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)


class Status(Base):
    __tablename__ = "status"

    status_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status_name: Mapped[str] = mapped_column(String(50), nullable=False)


class Priority(Base):
    __tablename__ = "priority"

    priority_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    priority_name: Mapped[str] = mapped_column(String(50), nullable=False)


class Account(Base):
    __tablename__ = "account"

    account_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Issue(Base):
    __tablename__ = "issue"

    issue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("project.project_id"), nullable=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="관리자")
    issue_description: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_date: Mapped[date | None] = mapped_column(Date, nullable=False)
    phase_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("occurrence_phase.phase_id"), nullable=True)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("location.location_id"), nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    production_tech_owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("production_tech_owner.owner_id"), nullable=True)
    status_id: Mapped[int] = mapped_column(Integer, ForeignKey("status.status_id"), nullable=False)
    temp_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_long_term: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("priority.priority_id"), nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    root_countermeasure: Mapped[str | None] = mapped_column(Text, nullable=True)
    purchase_request_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    object_insert: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )


class IssueImage(Base):
    __tablename__ = "issue_image"

    image_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    issue_id: Mapped[int] = mapped_column(Integer, ForeignKey("issue.issue_id"), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)


class IssueResponsibleDept(Base):
    __tablename__ = "issue_responsible_dept"

    issue_id: Mapped[int] = mapped_column(ForeignKey("issue.issue_id", ondelete="CASCADE"), primary_key=True)
    dept_id: Mapped[int] = mapped_column(ForeignKey("responsible_dept.dept_id"), primary_key=True)


class IssueTechDept(Base):
    __tablename__ = "issue_tech_dept"

    issue_id: Mapped[int] = mapped_column(ForeignKey("issue.issue_id", ondelete="CASCADE"), primary_key=True)
    dept_id: Mapped[int] = mapped_column(ForeignKey("tech_dept.dept_id"), primary_key=True)


class IssueFieldConfig(Base):
    __tablename__ = "issue_field_config"

    field_key: Mapped[str] = mapped_column(String(100), primary_key=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    show_in_list: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    list_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)
    option_source: Mapped[str | None] = mapped_column(String(100), nullable=True)


__all__ = [
    "Account",
    "Project",
    "OccurrencePhase",
    "Location",
    "ResponsibleDept",
    "TechDept",
    "ProductionTechOwner",
    "Status",
    "Priority",
    "Issue",
    "IssueImage",
    "IssueResponsibleDept",
    "IssueTechDept",
    "IssueFieldConfig",
]
