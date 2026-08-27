from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
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


class IssueMutationPayload(BaseModel):
    values: dict[str, Any] = Field(default_factory=dict)


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


def _serialize_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _is_required_issue_field(field_key: str) -> bool:
    column = Issue.__table__.columns.get(field_key)
    if column is None:
        return False

    if field_key in {"issue_id", "created_at", "updated_at"}:
        return False

    return bool(column.nullable is False and column.default is None and column.server_default is None)


def _get_editable_fields(field_config: list[dict[str, Any]]) -> list[dict[str, Any]]:
    editable: list[dict[str, Any]] = []
    for field in sorted(
        field_config,
        key=lambda item: (_to_int(item.get("detail_order"), 9999), str(item.get("field_key", ""))),
    ):
        key = field.get("field_key")
        if not isinstance(key, str):
            continue
        if key in {"issue_id", "created_at", "updated_at"}:
            continue
        if key not in Issue.__table__.columns.keys():
            continue
        editable.append(field)
    return editable


def _coerce_input_value(input_type: str, value: Any) -> Any:
    if value is None or value == "":
        return None

    normalized_type = str(input_type or "text")

    if normalized_type in {"number", "dropdown"}:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"Invalid numeric value: {value}") from exc

    if normalized_type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "1", "yes", "y"}:
                return True
            if lowered in {"false", "0", "no", "n"}:
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        raise HTTPException(status_code=400, detail=f"Invalid boolean value: {value}")

    if normalized_type == "date":
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=f"Invalid date value: {value}") from exc
        raise HTTPException(status_code=400, detail=f"Invalid date value: {value}")

    return str(value)


def _build_issue_payload_values(
    payload_values: dict[str, Any],
    editable_fields: list[dict[str, Any]],
    *,
    is_create: bool,
) -> dict[str, Any]:
    editable_map = {
        str(field.get("field_key")): field
        for field in editable_fields
        if isinstance(field.get("field_key"), str)
    }
    normalized_values: dict[str, Any] = {}

    for key, raw_value in payload_values.items():
        field = editable_map.get(str(key))
        if not field:
            continue

        input_type = str(field.get("input_type") or "text")
        normalized_values[str(key)] = _coerce_input_value(input_type, raw_value)

    if "is_long_term" not in normalized_values and is_create:
        normalized_values["is_long_term"] = False

    required_fields = [
        str(field.get("field_key"))
        for field in editable_fields
        if isinstance(field.get("field_key"), str) and _is_required_issue_field(str(field.get("field_key")))
    ]

    missing_fields = [
        key
        for key in required_fields
        if key not in normalized_values or normalized_values.get(key) is None
    ]
    if missing_fields and is_create:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")

    return normalized_values


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


@router.get("/{issue_id}/form")
def get_issue_form_data(issue_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(Issue, issue_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    field_config_rows = db.execute(select(IssueFieldConfig)).scalars().all()
    field_config = [_field_config_to_dict(row) for row in field_config_rows]
    editable_fields = _get_editable_fields(field_config)

    options_map = _build_options_map_from_db(db, field_config)

    fields: list[dict[str, Any]] = []
    for field in editable_fields:
        key = str(field.get("field_key"))
        source = field.get("option_source") if isinstance(field.get("option_source"), str) else None
        options = options_map.get(source, []) if source else []

        fields.append(
            {
                "key": key,
                "label": field.get("label", key),
                "input_type": field.get("input_type") or "text",
                "option_source": source,
                "detail_order": field.get("detail_order"),
                "required": _is_required_issue_field(key),
                "value": _serialize_value(getattr(target, key)),
                "options": options,
            }
        )

    return {
        "issue_id": issue_id,
        "fields": fields,
        "options_map": options_map,
    }


@router.post("")
def create_issue(payload: IssueMutationPayload, db: Session = Depends(get_db)) -> dict[str, Any]:
    field_config_rows = db.execute(select(IssueFieldConfig)).scalars().all()
    field_config = [_field_config_to_dict(row) for row in field_config_rows]
    editable_fields = _get_editable_fields(field_config)

    values = _build_issue_payload_values(payload.values, editable_fields, is_create=True)

    issue = Issue(**values)
    db.add(issue)
    db.commit()
    db.refresh(issue)

    return {
        "issue_id": issue.issue_id,
    }


@router.put("/{issue_id}")
def update_issue(issue_id: int, payload: IssueMutationPayload, db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(Issue, issue_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    field_config_rows = db.execute(select(IssueFieldConfig)).scalars().all()
    field_config = [_field_config_to_dict(row) for row in field_config_rows]
    editable_fields = _get_editable_fields(field_config)

    values = _build_issue_payload_values(payload.values, editable_fields, is_create=False)
    if not values:
        return {"issue_id": issue_id}

    for key, value in values.items():
        setattr(target, key, value)

    db.add(target)
    db.commit()
    db.refresh(target)

    return {
        "issue_id": target.issue_id,
    }


@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    target = db.get(Issue, issue_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    image_rows = db.execute(select(IssueImage).where(IssueImage.issue_id == issue_id)).scalars().all()
    for image in image_rows:
        db.delete(image)

    db.delete(target)
    db.commit()
    return {"issue_id": issue_id}
