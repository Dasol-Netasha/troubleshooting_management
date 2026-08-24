from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Issue,
    IssueFieldConfig,
    Location,
    OccurrencePhase,
    Priority,
    ProductionTechOwner,
    Project,
    ResponsibleDept,
    Status,
    TechDept,
)

router = APIRouter(prefix="/issues", tags=["issues"])

OPTION_SOURCE_CONFIG: dict[str, tuple[type, str, str]] = {
    "project": (Project, "project_id", "project_name"),
    "occurrence_phase": (OccurrencePhase, "phase_id", "phase_name"),
    "location": (Location, "location_id", "location_name"),
    "responsible_dept": (ResponsibleDept, "dept_id", "dept_name"),
    "tech_dept": (TechDept, "dept_id", "dept_name"),
    "production_tech_owner": (ProductionTechOwner, "owner_id", "owner_name"),
    "status": (Status, "status_id", "status_name"),
    "priority": (Priority, "priority_id", "priority_name"),
}


def _sort_list_fields(field_config: list[dict[str, Any]]) -> list[dict[str, Any]]:
    visible_fields = [field for field in field_config if field.get("show_in_list") is True]
    return sorted(visible_fields, key=lambda field: field.get("list_order") or 9999)


def _fetch_option_rows(db: Session, source_name: str) -> list[dict[str, Any]]:
    config = OPTION_SOURCE_CONFIG.get(source_name)
    if not config:
        return []

    model_type, value_field, label_field = config
    stmt = select(getattr(model_type, value_field), getattr(model_type, label_field)).order_by(
        getattr(model_type, label_field)
    )
    rows = db.execute(stmt).all()
    return [{"value": row[0], "label": row[1]} for row in rows]


def _build_options_map_from_db(db: Session, field_config: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sources = {
        field.get("option_source")
        for field in field_config
        if isinstance(field.get("option_source"), str) and field.get("option_source")
    }
    return {source: _fetch_option_rows(db, source) for source in sorted(sources)}


def _coerce_field_config(row: IssueFieldConfig) -> dict[str, Any]:
    return {
        "field_key": row.field_key,
        "label": row.label,
        "show_in_list": bool(row.show_in_list),
        "list_order": row.list_order,
        "detail_order": row.detail_order,
        "input_type": row.input_type,
        "option_source": row.option_source,
    }


def _issue_to_dict(issue: Issue) -> dict[str, Any]:
    return {column.name: getattr(issue, column.name) for column in Issue.__table__.columns}


def _attach_field_options(
    fields: list[dict[str, Any]],
    options_map: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    enriched_fields: list[dict[str, Any]] = []

    for field in fields:
        source = field.get("option_source")
        next_field = dict(field)

        if field.get("input_type") == "dropdown" and isinstance(source, str) and source:
            next_field["options"] = options_map.get(source, [])
        else:
            next_field["options"] = []

        enriched_fields.append(next_field)

    return enriched_fields


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _match_value(issue_value: Any, filter_value: Any, input_type: str) -> bool:
    if filter_value is None:
        return True

    if isinstance(filter_value, str) and filter_value.strip() == "":
        return True

    if input_type in {"text", "textarea"}:
        return _normalize_text(filter_value) in _normalize_text(issue_value)

    if input_type == "boolean":
        return bool(issue_value) is bool(filter_value)

    if input_type in {"number", "dropdown"}:
        return str(issue_value) == str(filter_value)

    if input_type == "date":
        return str(issue_value or "") == str(filter_value)

    return str(issue_value) == str(filter_value)


def _apply_filters(
    issues: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    filters: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not filters:
        return issues

    field_meta = {field.get("field_key"): field for field in fields}
    filtered: list[dict[str, Any]] = []

    for issue in issues:
        include = True
        for key, raw_filter_value in filters.items():
            field = field_meta.get(key)
            if not field:
                continue

            input_type = str(field.get("input_type") or "text")
            if not _match_value(issue.get(key), raw_filter_value, input_type):
                include = False
                break

        if include:
            filtered.append(issue)

    return filtered


@router.get("/list-page")
def get_issue_list_page_data(
    filters: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    field_config_rows = db.execute(
        select(IssueFieldConfig).order_by(IssueFieldConfig.list_order.asc().nulls_last())
    ).scalars().all()
    field_config = [_coerce_field_config(row) for row in field_config_rows]

    issue_rows = db.execute(select(Issue).order_by(Issue.issue_id)).scalars().all()
    issues = [_issue_to_dict(issue) for issue in issue_rows]

    list_fields = _sort_list_fields(field_config)
    options_map = _build_options_map_from_db(db, field_config)
    fields_with_options = _attach_field_options(list_fields, options_map)

    parsed_filters: dict[str, Any] | None = None
    if filters:
        try:
            parsed = json.loads(filters)
            if isinstance(parsed, dict):
                parsed_filters = parsed
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="filters must be valid JSON object") from exc

    filtered_rows = _apply_filters(issues, list_fields, parsed_filters)

    return {
        "fields": fields_with_options,
        "rows": filtered_rows,
        "options_map": options_map,
        "total_count": len(filtered_rows),
    }
