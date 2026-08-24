from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Issue,
    IssueFieldConfig,
    IssueImage,
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


def _fetch_option_rows(db: Session, source_name: str) -> dict[str, str]:
    config = OPTION_SOURCE_CONFIG.get(source_name)
    if not config:
        return {}

    model_type, value_field, label_field = config
    stmt = select(getattr(model_type, value_field), getattr(model_type, label_field)).order_by(
        getattr(model_type, label_field)
    )
    rows = db.execute(stmt).all()
    return {str(row[0]): str(row[1]) for row in rows}


def _build_options_map_from_db(db: Session, field_config: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sources = {
        field.get("option_source")
        for field in field_config
        if isinstance(field.get("option_source"), str) and field.get("option_source")
    }

    options_map: dict[str, list[dict[str, Any]]] = {}
    for source in sorted(sources):
        rows = _fetch_option_rows(db, source)
        options_map[source] = [{"value": value, "label": label} for value, label in rows.items()]
    return options_map


def _build_field_config_map(field_config: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for field in field_config:
        field_key = field.get("field_key")
        if isinstance(field_key, str) and field_key:
            result[field_key] = field
    return result


def _build_option_lookup(options_map: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for source, options in options_map.items():
        source_map: dict[str, Any] = {}
        for option in options or []:
            source_map[str(option.get("value"))] = option.get("label")
        lookup[source] = source_map
    return lookup


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _resolve_display_value(raw_value: Any, input_type: str, option_source: str | None, option_lookup: dict[str, dict[str, Any]]) -> Any:
    if raw_value is None or raw_value == "":
        return "-"

    if isinstance(raw_value, (date, datetime)):
        return raw_value.isoformat()

    if input_type == "boolean":
        return "Yes" if bool(raw_value) else "No"

    if option_source:
        resolved = option_lookup.get(option_source, {}).get(str(raw_value))
        if resolved is not None:
            return resolved

    return raw_value


def _field_config_to_dict(row: IssueFieldConfig) -> dict[str, Any]:
    return {
        "field_key": row.field_key,
        "label": row.label,
        "show_in_list": bool(row.show_in_list),
        "list_order": row.list_order,
        "detail_order": row.detail_order,
        "input_type": row.input_type,
        "option_source": row.option_source,
    }


@router.get("/{issue_id}")
def get_issue_detail(issue_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(Issue, issue_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    field_config_rows = db.execute(select(IssueFieldConfig)).scalars().all()
    field_config = [_field_config_to_dict(row) for row in field_config_rows]

    options_map = _build_options_map_from_db(db, field_config)
    option_lookup = _build_option_lookup(options_map)
    field_config_map = _build_field_config_map(field_config)

    fields: list[dict[str, Any]] = []
    for config in sorted(
        field_config,
        key=lambda item: (_to_int(item.get("detail_order"), 9999), str(item.get("field_key", ""))),
    ):
        key = config.get("field_key")
        if not isinstance(key, str):
            continue

        if key not in Issue.__table__.columns.keys():
            continue

        raw_value = getattr(target, key)
        meta = field_config_map.get(key, {})
        option_source = meta.get("option_source") if isinstance(meta.get("option_source"), str) else None
        input_type = str(meta.get("input_type") or "text")
        detail_order = _to_int(meta.get("detail_order"), 9999)

        fields.append(
            {
                "key": key,
                "label": meta.get("label", key),
                "value": _resolve_display_value(raw_value, input_type, option_source, option_lookup),
                "detail_order": detail_order,
            }
        )

    image_rows = db.execute(select(IssueImage).where(IssueImage.issue_id == issue_id)).scalars().all()
    images: list[dict[str, Any]] = []
    for image in image_rows:
        images.append(
            {
                "image_id": image.image_id,
                "image_path": image.image_path,
            }
        )

    return {
        "issue_id": issue_id,
        "fields": fields,
        "images": images,
    }
