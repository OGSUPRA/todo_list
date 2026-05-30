from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


async def save_avatar(file: UploadFile, user_id: uuid.UUID) -> str:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неподдерживаемый формат изображения")

    target_dir = Path(settings.media_root) / "avatars"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{user_id}{extension}"
    content = await file.read()
    target_path.write_bytes(content)
    return f"/media/avatars/{target_path.name}"
