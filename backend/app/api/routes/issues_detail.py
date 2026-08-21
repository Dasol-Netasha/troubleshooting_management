from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

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


def _resolve_display_value(raw_value: Any, input_type: str, option_source: str | None, option_lookup: dict[str, dict[str, Any]]) -> Any:
    if raw_value is None or raw_value == "":
        return "-"

    if input_type == "boolean":
        return "Yes" if bool(raw_value) else "No"

    if option_source:
        resolved = option_lookup.get(option_source, {}).get(str(raw_value))
        if resolved is not None:
            return resolved

    return raw_value


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@router.get("/{issue_id}")
def get_issue_detail(issue_id: int) -> dict[str, Any]:
    field_config = _load_json("issue_field_config.json")
    issues = _load_json("issue.json")
    issue_images = _load_json("issue_image.json")

    if not isinstance(field_config, list) or not isinstance(issues, list) or not isinstance(issue_images, list):
        raise HTTPException(status_code=500, detail="Invalid issue temporary db structure")

    target = next((issue for issue in issues if int(issue.get("issue_id", -1)) == issue_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Issue not found")

    options_map = _build_options_map(field_config)
    option_lookup = _build_option_lookup(options_map)
    field_config_map = _build_field_config_map(field_config)

    fields: list[dict[str, Any]] = []
    for key, raw_value in target.items():
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

    fields.sort(key=lambda item: (item.get("detail_order", 9999), str(item.get("key", ""))))

    images: list[dict[str, Any]] = []
    for image in issue_images:
        try:
            if int(image.get("issue_id", -1)) != issue_id:
                continue
        except (TypeError, ValueError):
            continue

        images.append(
            {
                "image_id": image.get("image_id"),
                "image_path": image.get("image_path"),
            }
        )

    return {
        "issue_id": issue_id,
        "fields": fields,
        "images": images,
    }