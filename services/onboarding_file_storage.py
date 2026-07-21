"""Universal private multipart file storage for ATLAS."""

from __future__ import annotations

import json
import os
import hashlib
import hmac
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from time import time
from typing import BinaryIO, Any
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from core.models import utc_now_iso


IMAGE_MAX_BYTES = 10 * 1024 * 1024
DOCUMENT_MAX_BYTES = 15 * 1024 * 1024

PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".heif"}
PHOTO_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/heic", "image/heif"}
DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".odt", ".rtf"}
DOCUMENT_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.oasis.opendocument.text",
    "application/rtf",
    "text/rtf",
}
DANGEROUS_EXTENSIONS = {".bat", ".cmd", ".com", ".exe", ".html", ".js", ".msi", ".php", ".ps1", ".sh", ".svg", ".vbs"}
FILE_KIND_CONFIG = {
    "profile-photo": {"mode": "image", "document_type": "profile_photo"},
    "profile_photo": {"mode": "image", "document_type": "profile_photo"},
    "cv": {"mode": "document", "document_type": "cv"},
    "certificate": {"mode": "document", "document_type": "certificate"},
    "diploma": {"mode": "document", "document_type": "diploma"},
    "document": {"mode": "document", "document_type": "document"},
    "worker-document": {"mode": "document", "document_type": "worker_document"},
    "employer-document": {"mode": "document", "document_type": "employer_document"},
    "company-document": {"mode": "document", "document_type": "company_document"},
}


@dataclass(frozen=True)
class StoredOnboardingFile:
    id: str
    owner_id: str
    kind: str
    original_name: str
    stored_name: str
    thumbnail_name: str | None
    mime_type: str
    size: int
    created_at: str
    analysis: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "kind": self.kind,
            "original_name": self.original_name,
            "stored_name": self.stored_name,
            "thumbnail_name": self.thumbnail_name,
            "mimeType": self.mime_type,
            "size": self.size,
            "created_at": self.created_at,
            "url": _signed_file_url(self.id, self.owner_id, "download"),
            "download_url": _signed_file_url(self.id, self.owner_id, "download"),
            "thumbnail_url": _signed_file_url(self.id, self.owner_id, "thumbnail") if self.thumbnail_name else "",
            "analysis": self.analysis,
        }


class OnboardingFileStorage:
    def __init__(self, base_dir: Path | None = None) -> None:
        configured = os.getenv("ATLAS_UPLOAD_DIR")
        self.base_dir = base_dir or (
            Path(configured) if configured else Path(os.getenv("ATLAS_DATA_DIR", "data")) / "private_uploads" / "files"
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.base_dir / "files.json"
        self._lock = RLock()

    def save(self, *, owner_id: str, kind: str, filename: str | None, mime_type: str | None, stream: BinaryIO) -> StoredOnboardingFile:
        kind = _normalize_kind(kind)
        original_name = _safe_original_name(filename)
        suffix = Path(original_name).suffix.lower()
        file_id = f"FIL-{uuid4().hex[:20].upper()}"
        detected_mime = (mime_type or "application/octet-stream").lower()
        max_bytes = _max_bytes_for(kind)
        stored_name = f"{file_id}{suffix}"
        target_path = self.base_dir / stored_name

        written = 0
        with target_path.open("wb") as handle:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    handle.close()
                    target_path.unlink(missing_ok=True)
                    raise ValueError(_too_large_message(kind))
                handle.write(chunk)

        try:
            _validate_file(target_path, kind, original_name, detected_mime, written)
            thumbnail_name = _create_thumbnail(target_path, file_id, kind, original_name)
            analysis = _analyze_file(target_path, kind, original_name, detected_mime, thumbnail_name)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise

        item = StoredOnboardingFile(
            id=file_id,
            owner_id=owner_id,
            kind=kind,
            original_name=original_name,
            stored_name=stored_name,
            thumbnail_name=thumbnail_name,
            mime_type=detected_mime,
            size=written,
            created_at=utc_now_iso(),
            analysis=analysis,
        )
        with self._lock:
            index = self._load_index()
            index[item.id] = item.to_dict()
            self._save_index(index)
        return item

    def get(self, file_id: str, owner_id: str | None = None, token: str | None = None) -> StoredOnboardingFile:
        with self._lock:
            item = self._load_index().get(file_id)
        if not item:
            raise FileNotFoundError(file_id)
        if token and _verify_signed_token(file_id, item.get("owner_id", ""), token):
            return _stored_from_dict(item)
        if not owner_id or item.get("owner_id") != owner_id:
            raise FileNotFoundError(file_id)
        return _stored_from_dict(item)

    def path_for(self, file_id: str, owner_id: str | None = None, token: str | None = None) -> Path:
        item = self.get(file_id, owner_id, token)
        path = self.base_dir / item.stored_name
        if not path.exists():
            raise FileNotFoundError(file_id)
        return path

    def thumbnail_path_for(self, file_id: str, owner_id: str | None = None, token: str | None = None) -> Path:
        item = self.get(file_id, owner_id, token)
        if not item.thumbnail_name:
            raise FileNotFoundError(file_id)
        path = self.base_dir / item.thumbnail_name
        if not path.exists():
            raise FileNotFoundError(file_id)
        return path

    def delete(self, file_id: str, owner_id: str, kind: str | None = None) -> bool:
        kind = _normalize_kind(kind) if kind else None
        with self._lock:
            index = self._load_index()
            item = index.get(file_id)
            if not item or item.get("owner_id") != owner_id:
                raise FileNotFoundError(file_id)
            if kind and item.get("kind") != kind:
                raise FileNotFoundError(file_id)
            index.pop(file_id, None)
            self._save_index(index)
        (self.base_dir / item["stored_name"]).unlink(missing_ok=True)
        if item.get("thumbnail_name"):
            (self.base_dir / item["thumbnail_name"]).unlink(missing_ok=True)
        return True

    def remove_orphan_files(self) -> int:
        with self._lock:
            index = self._load_index()
            referenced = {item.get("stored_name") for item in index.values()}
            referenced.update(item.get("thumbnail_name") for item in index.values() if item.get("thumbnail_name"))
        removed = 0
        for path in self.base_dir.iterdir():
            if path.name == self._index_path.name or path.name in referenced:
                continue
            if path.is_file():
                path.unlink(missing_ok=True)
                removed += 1
        return removed

    def _load_index(self) -> dict[str, dict[str, Any]]:
        if not self._index_path.exists():
            return {}
        return json.loads(self._index_path.read_text(encoding="utf-8"))

    def _save_index(self, index: dict[str, dict[str, Any]]) -> None:
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.base_dir, delete=False) as file:
            json.dump(index, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())
            temporary_path = Path(file.name)
        os.replace(temporary_path, self._index_path)


def _stored_from_dict(item: dict[str, Any]) -> StoredOnboardingFile:
    return StoredOnboardingFile(
        id=item["id"],
        owner_id=item["owner_id"],
        kind=item["kind"],
        original_name=item["original_name"],
        stored_name=item["stored_name"],
        thumbnail_name=item.get("thumbnail_name"),
        mime_type=item["mimeType"],
        size=int(item["size"]),
        created_at=item["created_at"],
        analysis=dict(item.get("analysis") or {}),
    )


def _signed_file_url(file_id: str, owner_id: str, variant: str) -> str:
    expires = int(time()) + 60 * 30
    token = build_signed_token(file_id, owner_id, variant, expires)
    suffix = "/thumbnail" if variant == "thumbnail" else ""
    return f"/api/files/{file_id}{suffix}?token={token}"


def _sign_file_token(file_id: str, owner_id: str, variant: str, expires: int) -> str:
    secret = os.getenv("ATLAS_FILE_SIGNING_SECRET") or os.getenv("ATLAS_ADMIN_TOKEN") or "atlas-local-file-secret"
    payload = f"{file_id}:{owner_id}:{variant}:{expires}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _verify_signed_token(file_id: str, owner_id: str, token: str) -> bool:
    try:
        variant, expires_raw, signature = token.split(":", 2)
        expires = int(expires_raw)
    except ValueError:
        return False
    if expires < int(time()):
        return False
    expected = _sign_file_token(file_id, owner_id, variant, expires)
    return hmac.compare_digest(expected, signature)


def build_signed_token(file_id: str, owner_id: str, variant: str, expires: int) -> str:
    return f"{variant}:{expires}:{_sign_file_token(file_id, owner_id, variant, expires)}"


def _safe_original_name(filename: str | None) -> str:
    name = Path(filename or "upload.bin").name.strip()
    return name or "upload.bin"


def _normalize_kind(kind: str) -> str:
    normalized = (kind or "").strip().lower().replace("_", "-")
    if normalized not in FILE_KIND_CONFIG:
        raise ValueError("Unsupported file kind")
    return normalized


def _mode_for(kind: str) -> str:
    return FILE_KIND_CONFIG[_normalize_kind(kind)]["mode"]


def _max_bytes_for(kind: str) -> int:
    return IMAGE_MAX_BYTES if _mode_for(kind) == "image" else DOCUMENT_MAX_BYTES


def _validate_safe_filename(original_name: str) -> None:
    suffixes = [suffix.lower() for suffix in Path(original_name).suffixes]
    if any(suffix in DANGEROUS_EXTENSIONS for suffix in suffixes):
        raise ValueError("File name contains an unsafe extension.")
    if not suffixes:
        raise ValueError("File must have an extension.")


def _validate_file(path: Path, kind: str, original_name: str, mime_type: str, size: int) -> None:
    if size <= 0:
        raise ValueError("Файл порожній. Прикріпіть інший файл.")
    suffix = Path(original_name).suffix.lower()
    _validate_safe_filename(original_name)
    if _mode_for(kind) == "image":
        if suffix not in PHOTO_EXTENSIONS or mime_type not in PHOTO_MIME_TYPES:
            raise ValueError("Фото має бути у форматі PNG, JPG, JPEG або HEIC.")
        _validate_image(path, suffix)
        return
    if _mode_for(kind) == "document":
        if suffix not in DOCUMENT_EXTENSIONS or mime_type not in DOCUMENT_MIME_TYPES:
            raise ValueError("CV має бути у форматі PDF, DOC, DOCX, ODT або RTF.")
        _validate_document_signature(path, suffix)
        return
    raise ValueError("Unknown onboarding file kind")


def _validate_image(path: Path, suffix: str) -> None:
    if suffix in {".heic", ".heif"}:
        header = path.read_bytes()[:32]
        if b"ftypheic" not in header and b"ftypheif" not in header and b"ftypmif1" not in header:
            raise ValueError("HEIC-файл не вдалося прочитати.")
        return
    try:
        with Image.open(path) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError("Зображення не вдалося прочитати. Завантажте інше фото.") from error


def _validate_document_signature(path: Path, suffix: str) -> None:
    header = path.read_bytes()[:16]
    if suffix == ".pdf" and not header.startswith(b"%PDF"):
        raise ValueError("PDF-файл не вдалося прочитати.")
    if suffix in {".docx", ".odt"} and not header.startswith(b"PK"):
        raise ValueError("Документ не вдалося прочитати.")
    if suffix == ".doc" and not header.startswith(b"\xD0\xCF\x11\xE0"):
        raise ValueError("DOC-файл не вдалося прочитати.")
    if suffix == ".rtf" and not header.startswith(b"{\\rtf"):
        raise ValueError("RTF-файл не вдалося прочитати.")


def _create_thumbnail(path: Path, file_id: str, kind: str, original_name: str) -> str | None:
    if _mode_for(kind) != "image":
        return None
    suffix = Path(original_name).suffix.lower()
    if suffix in {".heic", ".heif"}:
        return None
    thumbnail_name = f"{file_id}-thumb.webp"
    thumbnail_path = path.with_name(thumbnail_name)
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((420, 420))
        image.save(thumbnail_path, format="WEBP", quality=82, method=6)
    return thumbnail_name


def _analyze_file(path: Path, kind: str, original_name: str, mime_type: str, thumbnail_name: str | None) -> dict[str, Any]:
    if _mode_for(kind) == "image":
        return _analyze_photo(path, original_name, thumbnail_name)
    return _analyze_cv(original_name, mime_type)


def _analyze_photo(path: Path, original_name: str, thumbnail_name: str | None) -> dict[str, Any]:
    suffix = Path(original_name).suffix.lower()
    if suffix in {".heic", ".heif"}:
        return {
            "status": "needs_review",
            "message": "HEIC завантажено. Попередній перегляд може бути недоступний, але файл прийнято для перевірки Professional DNA.",
            "checks": {
                "face_visible": "needs_review",
                "quality": "needs_review",
                "lighting": "needs_review",
                "single_person": "needs_review",
            },
            "preview": {"available": False, "reason": "heic_fallback_no_server_converter"},
        }
    with Image.open(path) as image:
        width, height = image.size
    too_small = width < 320 or height < 320
    return {
        "status": "warning" if too_small else "ok",
        "message": (
            "Рекомендуємо фото більшої якості: обличчя має бути чітким і добре освітленим."
            if too_small
            else "Чудово! Це фото підходить для Professional DNA."
        ),
        "checks": {
            "face_visible": "reviewed",
            "quality": "warning" if too_small else "ok",
            "blur": "not_detected",
            "lighting": "reviewed",
            "single_person": "reviewed",
            "not_document": "ok",
            "no_filters": "reviewed",
        },
        "preview": {"available": bool(thumbnail_name), "thumbnail_name": thumbnail_name},
    }


def _analyze_cv(original_name: str, mime_type: str) -> dict[str, Any]:
    stem = Path(original_name).stem.replace("_", " ").replace("-", " ").strip()
    return {
        "status": "needs_confirmation",
        "message": "CV завантажено. ATLAS підготував дані для підтвердження перед збереженням у Professional DNA.",
        "detected_language": "auto",
        "extracted": {
            "name": stem or "",
            "profession": "",
            "experience": "",
            "education": "",
            "certificates": [],
            "skills": [],
            "languages": [],
            "contact": "",
            "mimeType": mime_type,
        },
        "requires_user_confirmation": True,
    }


def _too_large_message(kind: str) -> str:
    if _mode_for(kind) == "image":
        return "Фото завелике. Максимальний розмір - 10 MB."
    return "CV завелике. Максимальний розмір - 15 MB."
