from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
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

router = APIRouter(prefix="/options", tags=["options"])
MANAGED_OPTION_INPUT_TYPES = {"dropdown", "multi_dropdown"}

OPTION_TABLE_CONFIG: dict[str, dict[str, Any]] = {
    "project": {
        "label": "프로젝트",
        "model": Project,
        "id_field": "project_id",
        "name_field": "project_name",
    },
    "occurrence_phase": {
        "label": "발생시점",
        "model": OccurrencePhase,
        "id_field": "phase_id",
        "name_field": "phase_name",
    },
    "location": {
        "label": "발생위치",
        "model": Location,
        "id_field": "location_id",
        "name_field": "location_name",
    },
    "responsible_dept": {
        "label": "책임부서",
        "model": ResponsibleDept,
        "id_field": "dept_id",
        "name_field": "dept_name",
    },
    "tech_dept": {
        "label": "기술부서",
        "model": TechDept,
        "id_field": "dept_id",
        "name_field": "dept_name",
    },
    "production_tech_owner": {
        "label": "생산기술담당자",
        "model": ProductionTechOwner,
        "id_field": "owner_id",
        "name_field": "owner_name",
    },
    "status": {
        "label": "현재상태",
        "model": Status,
        "id_field": "status_id",
        "name_field": "status_name",
    },
    "priority": {
        "label": "우선순위",
        "model": Priority,
        "id_field": "priority_id",
        "name_field": "priority_name",
    },
}


def _get_source_config(source: str) -> dict[str, Any]:
    config = OPTION_TABLE_CONFIG.get(source)
    if config is None:
        raise HTTPException(status_code=404, detail="Option source not found")
    return config


def _get_dropdown_source_labels(db: Session) -> dict[str, str]:
    rows = db.execute(
        select(IssueFieldConfig).order_by(IssueFieldConfig.detail_order.asc().nulls_last())
    ).scalars().all()

    source_labels: dict[str, str] = {}
    for row in rows:
        if str(row.input_type or "").strip().lower() not in MANAGED_OPTION_INPUT_TYPES:
            continue

        source = str(row.option_source or "").strip()
        if not source:
            continue

        if source not in OPTION_TABLE_CONFIG:
            continue

        if source not in source_labels:
            source_labels[source] = str(row.label or OPTION_TABLE_CONFIG[source]["label"])

    return source_labels


def _get_source_config_for_dropdown(db: Session, source: str) -> dict[str, Any]:
    source_labels = _get_dropdown_source_labels(db)
    if source not in source_labels:
        raise HTTPException(status_code=404, detail="Configured dropdown source not found")

    config = _get_source_config(source)
    return {
        **config,
        "label": source_labels[source],
    }


def _parse_label(payload: dict[str, Any]) -> str:
    raw_label = payload.get("label")
    label = str(raw_label or "").strip()
    if not label:
        raise HTTPException(status_code=400, detail="label is required")
    return label


@router.get("/sources")
def get_option_sources(db: Session = Depends(get_db)) -> dict[str, list[dict[str, str]]]:
    sources: list[dict[str, str]] = []

    source_labels = _get_dropdown_source_labels(db)

    for key, label in source_labels.items():
        sources.append(
            {
                "key": key,
                "label": label,
            }
        )

    sources.sort(key=lambda item: item["label"])
    return {"sources": sources}


@router.get("/{source}")
def list_options(source: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    config = _get_source_config_for_dropdown(db, source)
    model = config["model"]
    id_field = str(config["id_field"])
    name_field = str(config["name_field"])

    stmt = select(model).order_by(getattr(model, name_field))
    rows = db.execute(stmt).scalars().all()

    items = [
        {
            "id": getattr(row, id_field),
            "label": getattr(row, name_field),
        }
        for row in rows
    ]

    return {
        "source": source,
        "source_label": config["label"],
        "items": items,
    }


@router.post("/{source}")
def create_option(source: str, payload: dict[str, Any], db: Session = Depends(get_db)) -> dict[str, Any]:
    config = _get_source_config_for_dropdown(db, source)
    model = config["model"]
    id_field = str(config["id_field"])
    name_field = str(config["name_field"])
    label = _parse_label(payload)

    duplicate = db.execute(select(model).where(getattr(model, name_field) == label)).scalar_one_or_none()
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="label already exists")

    row = model(**{name_field: label})
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "source": source,
        "item": {
            "id": getattr(row, id_field),
            "label": getattr(row, name_field),
        },
    }


@router.put("/{source}/{item_id}")
def update_option(source: str, item_id: int, payload: dict[str, Any], db: Session = Depends(get_db)) -> dict[str, Any]:
    config = _get_source_config_for_dropdown(db, source)
    model = config["model"]
    id_field = str(config["id_field"])
    name_field = str(config["name_field"])
    label = _parse_label(payload)

    row = db.execute(select(model).where(getattr(model, id_field) == item_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Option item not found")

    duplicate = db.execute(
        select(model).where(
            getattr(model, name_field) == label,
            getattr(model, id_field) != item_id,
        )
    ).scalar_one_or_none()
    if duplicate is not None:
        raise HTTPException(status_code=409, detail="label already exists")

    setattr(row, name_field, label)
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "source": source,
        "item": {
            "id": getattr(row, id_field),
            "label": getattr(row, name_field),
        },
    }


@router.delete("/{source}/{item_id}")
def delete_option(source: str, item_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    config = _get_source_config_for_dropdown(db, source)
    model = config["model"]
    id_field = str(config["id_field"])

    row = db.execute(select(model).where(getattr(model, id_field) == item_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Option item not found")

    try:
        db.delete(row)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="해당 항목을 사용하는 이슈가 있어 삭제할 수 없습니다.") from exc

    return {
        "source": source,
        "deleted_id": item_id,
    }
