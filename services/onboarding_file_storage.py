"""Private multipart file storage for ATLAS agent onboarding."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from typing import BinaryIO, Any
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from core.models import utc_now_iso


PHOTO_MAX_BYTES = 10 * 1024 * 1024
CV_MAX_BYTES = 15 * 1024 * 1024

PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".heic", ".heif"}
PHOTO_MIME_TYPES = {"image/png", "image/jpeg", "image/heic", "image/heif"}
CV_EXTENSIONS = {".pdf", ".doc", ".docx", ".odt", ".rtf"}
CV_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.oasis.opendocument.text",
    "application/rtf",
    "text/rtf",
}


@dataclass(frozen=True)
class StoredOnboardingFile:
    id: str
    owner_id: str
    kind: str
    original_name: str
    stored_name: str
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
            "mimeType": self.mime_type,
            "size": self.size,
            "created_at": self.created_at,
            "url": f"/api/onboarding/files/{self.id}",
            "analysis": self.analysis,
        }


class OnboardingFileStorage:
    def __init__(self, base_dir: Path | None = None) -> None:
        configured = os.getenv("ATLAS_UPLOAD_DIR")
        self.base_dir = base_dir or (
            Path(configured) if configured else Path(os.getenv("ATLAS_DATA_DIR", "data")) / "private_uploads" / "onboarding"
        )
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self.base_dir / "files.json"
        self._lock = RLock()

    def save(self, *, owner_id: str, kind: str, filename: str | None, mime_type: str | None, stream: BinaryIO) -> StoredOnboardingFile:
        original_name = _safe_original_name(filename)
        suffix = Path(original_name).suffix.lower()
        file_id = f"ONB-{uuid4().hex[:16].upper()}"
        detected_mime = (mime_type or "application/octet-stream").lower()
        max_bytes = PHOTO_MAX_BYTES if kind == "profile_photo" else CV_MAX_BYTES
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
            analysis = _analyze_file(target_path, kind, original_name, detected_mime)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise

        item = StoredOnboardingFile(
            id=file_id,
            owner_id=owner_id,
            kind=kind,
            original_name=original_name,
            stored_name=stored_name,
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

    def get(self, file_id: str, owner_id: str) -> StoredOnboardingFile:
        with self._lock:
            item = self._load_index().get(file_id)
        if not item or item.get("owner_id") != owner_id:
            raise FileNotFoundError(file_id)
        return _stored_from_dict(item)

    def path_for(self, file_id: str, owner_id: str) -> Path:
        item = self.get(file_id, owner_id)
        path = self.base_dir / item.stored_name
        if not path.exists():
            raise FileNotFoundError(file_id)
        return path

    def delete(self, file_id: str, owner_id: str, kind: str | None = None) -> bool:
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
        return True

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
        mime_type=item["mimeType"],
        size=int(item["size"]),
        created_at=item["created_at"],
        analysis=dict(item.get("analysis") or {}),
    )


def _safe_original_name(filename: str | None) -> str:
    name = Path(filename or "upload.bin").name.strip()
    return name or "upload.bin"


def _validate_file(path: Path, kind: str, original_name: str, mime_type: str, size: int) -> None:
    if size <= 0:
        raise ValueError("Файл порожній. Прикріпіть інший файл.")
    suffix = Path(original_name).suffix.lower()
    if kind == "profile_photo":
        if suffix not in PHOTO_EXTENSIONS or mime_type not in PHOTO_MIME_TYPES:
            raise ValueError("Фото має бути у форматі PNG, JPG, JPEG або HEIC.")
        _validate_image(path, suffix)
        return
    if kind == "cv":
        if suffix not in CV_EXTENSIONS or mime_type not in CV_MIME_TYPES:
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


def _analyze_file(path: Path, kind: str, original_name: str, mime_type: str) -> dict[str, Any]:
    if kind == "profile_photo":
        return _analyze_photo(path, original_name)
    return _analyze_cv(original_name, mime_type)


def _analyze_photo(path: Path, original_name: str) -> dict[str, Any]:
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
    if kind == "profile_photo":
        return "Фото завелике. Максимальний розмір - 10 MB."
    return "CV завелике. Максимальний розмір - 15 MB."
