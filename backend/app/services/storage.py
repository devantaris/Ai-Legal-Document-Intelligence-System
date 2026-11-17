import abc
import shutil
from pathlib import Path
from typing import Any

from app.core.config import settings


class BaseStorage(abc.ABC):
    """Abstract storage backend for legal document retention."""

    @abc.abstractmethod
    def save(self, relative_path: str, data: bytes, mime: str = "application/octet-stream") -> str:
        """Save bytes to storage and return the stored file path or S3 key."""

    @abc.abstractmethod
    def read(self, file_path: str) -> bytes:
        """Read bytes from storage."""

    @abc.abstractmethod
    def delete(self, file_path: str) -> None:
        """Delete file and any parent directory if empty."""

    @abc.abstractmethod
    def exists(self, file_path: str) -> bool:
        """Check if file exists."""


class LocalStorage(BaseStorage):
    """Local filesystem storage with directory isolation."""

    def __init__(self, root: Path | None = None):
        self.root = root or settings.storage_path

    def _full_path(self, relative_path: str) -> Path:
        p = Path(relative_path)
        return p if p.is_absolute() else (self.root / p)

    def save(self, relative_path: str, data: bytes, mime: str = "application/octet-stream") -> str:
        target = self._full_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return str(target)

    def read(self, file_path: str) -> bytes:
        p = Path(file_path)
        if not p.is_absolute():
            p = self.root / p
        return p.read_bytes()

    def delete(self, file_path: str) -> None:
        p = Path(file_path)
        if not p.is_absolute():
            p = self.root / p
        if p.is_file():
            p.unlink()
        # Clean parent doc folder if empty
        if p.parent.is_dir() and not any(p.parent.iterdir()):
            shutil.rmtree(p.parent, ignore_errors=True)

    def exists(self, file_path: str) -> bool:
        p = Path(file_path)
        if not p.is_absolute():
            p = self.root / p
        return p.is_file()


class S3Storage(BaseStorage):
    """S3-compatible object storage (AWS S3, MinIO, Cloudflare R2, Ceph).

    Enforces server-side encryption (SSE-S3 / AES256) at rest for strict legal confidentiality.
    """

    def __init__(
        self,
        bucket: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "us-east-1",
    ):
        import boto3
        from botocore.config import Config

        self.bucket = bucket
        session = boto3.session.Session()
        self.client = session.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.client.create_bucket(Bucket=self.bucket)
            except Exception:
                pass

    def save(self, relative_path: str, data: bytes, mime: str = "application/octet-stream") -> str:
        key = relative_path.replace("\\", "/").lstrip("/")
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=mime,
            ServerSideEncryption="AES256",
        )
        return key

    def read(self, file_path: str) -> bytes:
        key = file_path.replace("\\", "/").lstrip("/")
        resp = self.client.get_object(Bucket=self.bucket, Key=key)
        return resp["Body"].read()

    def delete(self, file_path: str) -> None:
        key = file_path.replace("\\", "/").lstrip("/")
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception:
            pass

    def exists(self, file_path: str) -> bool:
        key = file_path.replace("\\", "/").lstrip("/")
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )


_storage_instance: BaseStorage | None = None


def get_storage() -> BaseStorage:
    global _storage_instance
    if _storage_instance is not None:
        return _storage_instance

    backend = getattr(settings, "STORAGE_BACKEND", "local").lower()
    if backend == "s3" and getattr(settings, "S3_BUCKET_NAME", None):
        _storage_instance = S3Storage(
            bucket=settings.S3_BUCKET_NAME,
            endpoint_url=getattr(settings, "S3_ENDPOINT_URL", None),
            access_key=getattr(settings, "S3_ACCESS_KEY", None),
            secret_key=getattr(settings, "S3_SECRET_KEY", None),
            region=getattr(settings, "S3_REGION", "us-east-1"),
        )
    else:
        _storage_instance = LocalStorage()
    return _storage_instance
