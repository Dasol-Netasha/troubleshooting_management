from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/issues", tags=["issues"])

DB_ROOT = Path(__file__).resolve().parents[4] / "temporary_db"


def _load_json(file_name: str) -> Any:
    file_path = DB_ROOT / file_name
    if not file_path.exists():
        raise HTTPException(status_code=500, detail=f"Missing temporary db file: {file_name}")

    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {file_name}") from exc


def _sort_list_fields(field_config: list[dict[str, Any]]) -> list[dict[str, Any]]:
    visible_fields = [field for field in field_config if field.get("show_in_list") is True]
    return sorted(visible_fields, key=lambda field: field.get("list_order") or 9999)


def _to_option_items(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in rows:
        keys = list(row.keys())
        value_key = next((key for key in keys if key.endswith("_id")), keys[0] if keys else None)
        label_key = next((key for key in keys if key.endswith("_name")), keys[1] if len(keys) > 1 else value_key)
        if not value_key or not label_key:
            continue

        items.append(
            {
                "value": row.get(value_key),
                "label": row.get(label_key),
            }
        )

    return items


def _build_options_map(field_config: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    sources = {
        field.get("option_source")
        for field in field_config
        if isinstance(field.get("option_source"), str) and field.get("option_source")
    }

    options_map: dict[str, list[dict[str, Any]]] = {}
    for source in sources:
        option_rows = _load_json(f"{source}.json")
        if isinstance(option_rows, list):
            options_map[source] = _to_option_items(option_rows)
        else:
            options_map[source] = []

    return options_map


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
def get_issue_list_page_data(filters: str | None = Query(default=None)) -> dict[str, Any]:
    field_config = _load_json("issue_field_config.json")
    issues = _load_json("issue.json")

    if not isinstance(field_config, list) or not isinstance(issues, list):
        raise HTTPException(status_code=500, detail="Invalid issue temporary db structure")

    list_fields = _sort_list_fields(field_config)
    options_map = _build_options_map(field_config)
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
