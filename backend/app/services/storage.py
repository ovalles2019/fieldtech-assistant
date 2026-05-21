import os
from pathlib import Path

import boto3
from botocore.client import Config

from app.config import settings


class StorageService:
    def __init__(self) -> None:
        self.local_root = Path(settings.local_storage_path)
        self.local_root.mkdir(parents=True, exist_ok=True)
        self._client = None

    @property
    def client(self):
        if self._client is None and not settings.use_local_storage:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                region_name=settings.s3_region,
                config=Config(signature_version="s3v4"),
            )
        return self._client

    def upload_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        if settings.use_local_storage:
            path = self.local_root / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return key
        assert self.client is not None
        self.client.put_object(Bucket=settings.s3_bucket, Key=key, Body=data, ContentType=content_type)
        return key

    def download_bytes(self, key: str) -> bytes:
        if settings.use_local_storage:
            return (self.local_root / key).read_bytes()
        assert self.client is not None
        obj = self.client.get_object(Bucket=settings.s3_bucket, Key=key)
        return obj["Body"].read()

    def exists(self, key: str) -> bool:
        if settings.use_local_storage:
            return (self.local_root / key).exists()
        assert self.client is not None
        try:
            self.client.head_object(Bucket=settings.s3_bucket, Key=key)
            return True
        except Exception:
            return False

    def health_check(self) -> bool:
        try:
            test_key = "_healthcheck.txt"
            self.upload_bytes(test_key, b"ok", "text/plain")
            return self.exists(test_key)
        except Exception:
            return False


storage_service = StorageService()
