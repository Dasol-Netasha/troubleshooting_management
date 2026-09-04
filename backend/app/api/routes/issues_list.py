from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Issue,
    IssueComment,
    IssueCommentReply,
    IssueFieldConfig,
    IssueResponsibleDept,
    IssueTechDept,
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

REQUIRED_FORM_FIELDS = {"project_id", "phase_id", "location_id", "author"}

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

MULTI_DROPDOWN_CONFIG: dict[str, tuple[type, str]] = {
    "responsible_dept_id": (IssueResponsibleDept, "dept_id"),
    "tech_dept_id": (IssueTechDept, "dept_id"),
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


def _is_required_issue_field(field_key: str) -> bool:
    if field_key in REQUIRED_FORM_FIELDS:
        return True

    column = Issue.__table__.columns.get(field_key)
    if column is None:
        return False

    if field_key in {"issue_id", "created_at", "updated_at"}:
        return False

    return bool(column.nullable is False and column.default is None and column.server_default is None)


def _issue_to_dict(issue: Issue) -> dict[str, Any]:
    return {column.name: getattr(issue, column.name) for column in Issue.__table__.columns}


def _attach_multi_dropdown_values(db: Session, issues: list[dict[str, Any]]) -> None:
    issue_ids = [issue["issue_id"] for issue in issues]
    if not issue_ids:
        return

    for field_key, (model_type, value_column) in MULTI_DROPDOWN_CONFIG.items():
        selected_rows = db.execute(
            select(model_type.issue_id, getattr(model_type, value_column)).where(model_type.issue_id.in_(issue_ids))
        ).all()
        values_by_issue = {issue_id: [] for issue_id in issue_ids}
        for issue_id, value in selected_rows:
            values_by_issue[issue_id].append(value)
        for issue in issues:
            issue[field_key] = values_by_issue[issue["issue_id"]]


def _attach_comment_counts(db: Session, issues: list[dict[str, Any]]) -> None:
    issue_ids = [issue["issue_id"] for issue in issues]
    if not issue_ids:
        return

    comment_counts = dict(
        db.execute(
            select(IssueComment.issue_id, func.count(IssueComment.comment_id))
            .where(IssueComment.issue_id.in_(issue_ids))
            .group_by(IssueComment.issue_id)
        ).all()
    )
    unanswered_counts = dict(
        db.execute(
            select(IssueComment.issue_id, func.count(IssueComment.comment_id))
            .outerjoin(IssueCommentReply, IssueCommentReply.comment_id == IssueComment.comment_id)
            .where(IssueComment.issue_id.in_(issue_ids), IssueCommentReply.reply_id.is_(None))
            .group_by(IssueComment.issue_id)
        ).all()
    )

    for issue in issues:
        issue_id = issue["issue_id"]
        issue["comment_count"] = comment_counts.get(issue_id, 0)
        issue["unanswered_comment_count"] = unanswered_counts.get(issue_id, 0)


def _attach_field_options(
    fields: list[dict[str, Any]],
    options_map: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    enriched_fields: list[dict[str, Any]] = []

    for field in fields:
        source = field.get("option_source")
        next_field = dict(field)

        if field.get("input_type") in {"dropdown", "multi_dropdown"} and isinstance(source, str) and source:
            next_field["options"] = options_map.get(source, [])
        else:
            next_field["options"] = []

        enriched_fields.append(next_field)

    return enriched_fields


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False
        return None

    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"", "all", "null", "none"}:
            return None
        if text in {"true", "1", "yes", "y", "t"}:
            return True
        if text in {"false", "0", "no", "n", "f"}:
            return False

    return None


def _match_value(issue_value: Any, filter_value: Any, input_type: str) -> bool:
    if filter_value is None:
        return True

    if isinstance(filter_value, str) and filter_value.strip() == "":
        return True

    if input_type in {"text", "textarea"}:
        return _normalize_text(filter_value) in _normalize_text(issue_value)

    if input_type == "boolean":
        normalized_filter = _to_bool(filter_value)
        if normalized_filter is None:
            return True

        normalized_issue = _to_bool(issue_value)
        if normalized_issue is None:
            normalized_issue = bool(issue_value)

        return normalized_issue is normalized_filter

    if input_type in {"number", "dropdown"}:
        return str(issue_value) == str(filter_value)

    if input_type == "multi_dropdown":
        return str(filter_value) in {str(value) for value in issue_value or []}

    if input_type == "date":
        return str(issue_value or "") == str(filter_value)

    return str(issue_value) == str(filter_value)


def _matches_unanswered_comment_filter(issue_value: Any, filter_value: Any) -> bool:
    normalized_filter = str(filter_value or "").strip().lower()
    if normalized_filter in {"", "all"}:
        return True

    has_unanswered_comments = int(issue_value or 0) > 0
    if normalized_filter in {"has", "있음"}:
        return has_unanswered_comments
    if normalized_filter in {"none", "없음"}:
        return not has_unanswered_comments
    return True


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

            if key == "unanswered_comment_count":
                if not _matches_unanswered_comment_filter(issue.get(key), raw_filter_value):
                    include = False
                    break
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
    _attach_multi_dropdown_values(db, issues)
    _attach_comment_counts(db, issues)

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


@router.get("/form-config")
def get_issue_form_config(db: Session = Depends(get_db)) -> dict[str, Any]:
    field_config_rows = db.execute(
        select(IssueFieldConfig).order_by(IssueFieldConfig.detail_order.asc().nulls_last())
    ).scalars().all()
    field_config = [_coerce_field_config(row) for row in field_config_rows]

    options_map = _build_options_map_from_db(db, field_config)

    fields: list[dict[str, Any]] = []
    for field in field_config:
        field_key = field.get("field_key")
        if not isinstance(field_key, str):
            continue

        if field_key == "completed_date":
            continue

        if field_key not in Issue.__table__.columns.keys() and field_key not in MULTI_DROPDOWN_CONFIG:
            continue

        source = field.get("option_source")
        options = options_map.get(source, []) if isinstance(source, str) and source else []

        fields.append(
            {
                "key": field_key,
                "label": field.get("label", field_key),
                "input_type": field.get("input_type") or "text",
                "option_source": source,
                "detail_order": field.get("detail_order"),
                "required": _is_required_issue_field(field_key),
                "options": options,
            }
        )

    return {
        "fields": fields,
        "options_map": options_map,
    }
