from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from urllib.parse import quote
from uuid import uuid4

from minio import Minio
from minio.error import S3Error
from starlette.datastructures import UploadFile

from app.config import settings


class MinioStorage:
    def __init__(self) -> None:
        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=bool(settings.minio_secure),
        )
        self._bucket = settings.minio_bucket
        self._bucket_ready = False
        self._bucket_lock = Lock()

    def _ensure_bucket(self) -> None:
        if self._bucket_ready:
            return

        with self._bucket_lock:
            if self._bucket_ready:
                return

            try:
                exists = self._client.bucket_exists(self._bucket)
                if not exists:
                    self._client.make_bucket(self._bucket)
                self._ensure_public_read_policy()
            except S3Error as exc:
                raise RuntimeError(f"Failed to ensure MinIO bucket '{self._bucket}': {exc}") from exc

            self._bucket_ready = True

    def _ensure_public_read_policy(self) -> None:
        # Allow anonymous read so <img src="..."> can fetch uploaded objects directly.
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self._bucket}/*"],
                }
            ],
        }
        self._client.set_bucket_policy(self._bucket, json.dumps(policy))

    def upload_issue_image(self, issue_id: int, image_file: UploadFile) -> str:
        self._ensure_bucket()

        extension = Path(image_file.filename or "").suffix
        object_name = f"issues/{issue_id}/{uuid4().hex}{extension}"
        content_type = image_file.content_type or "application/octet-stream"

        try:
            self._client.put_object(
                bucket_name=self._bucket,
                object_name=object_name,
                data=image_file.file,
                length=-1,
                part_size=10 * 1024 * 1024,
                content_type=content_type,
            )
        except S3Error as exc:
            raise RuntimeError(f"Failed to upload image to MinIO: {exc}") from exc

        return object_name

    def remove_object(self, object_name: str) -> None:
        if not object_name:
            return

        self._ensure_bucket()

        try:
            self._client.remove_object(self._bucket, object_name)
        except S3Error:
            # Ignore delete failures for missing/invalid objects to keep DB cleanup resilient.
            return

    def build_public_url(self, object_name: str) -> str:
        base_url = settings.minio_public_base_url.rstrip("/")
        safe_path = quote(object_name, safe="/")
        return f"{base_url}/{self._bucket}/{safe_path}"


_storage_singleton: MinioStorage | None = None


def get_minio_storage() -> MinioStorage:
    global _storage_singleton
    if _storage_singleton is None:
        _storage_singleton = MinioStorage()
    return _storage_singleton
