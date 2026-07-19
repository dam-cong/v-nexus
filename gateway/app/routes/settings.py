"""Settings routes: GET/PUT cấu hình LLM (admin only)."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import AppSetting
from app.auth import require_role
from app.config import settings

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class LLMConfigResponse(BaseModel):
    llm_mode: str
    llm_api_key: str
    llm_base_url: str
    llm_model: str
    updated_at: Optional[str] = None


class LLMConfigUpdate(BaseModel):
    llm_mode: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: Optional[str] = None


def _mask_key(key: str) -> str:
    """Ẩn API key, chỉ hiện 8 ký tự cuối."""
    if not key or len(key) <= 8:
        return key
    return "*" * (len(key) - 8) + key[-8:]


@router.get("/llm", response_model=LLMConfigResponse)
async def get_llm_config(
    user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_session),
):
    """Lấy cấu hình LLM hiện tại."""
    result = await db.execute(select(AppSetting))
    rows = result.scalars().all()
    kv = {row.key: row.value for row in rows}

    updated_at = None
    for row in rows:
        if row.updated_at:
            updated_at = row.updated_at.isoformat()

    return LLMConfigResponse(
        llm_mode=kv.get("llm_mode", settings.llm_mode),
        llm_api_key=_mask_key(kv.get("llm_api_key", settings.llm_api_key)),
        llm_base_url=kv.get("llm_base_url", settings.llm_base_url),
        llm_model=kv.get("llm_model", settings.llm_model),
        updated_at=updated_at,
    )


@router.put("/llm", response_model=LLMConfigResponse)
async def update_llm_config(
    body: LLMConfigUpdate,
    user: dict = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_session),
):
    """Cập nhật cấu hình LLM — lưu DB + apply runtime ngay."""
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Không có trường nào để cập nhật")

    # Lưu từng key vào DB
    for key, value in updates.items():
        result = await db.execute(select(AppSetting).where(AppSetting.key == key))
        row = result.scalar_one_or_none()
        if row:
            row.value = value
            row.updated_at = datetime.utcnow()
        else:
            db.add(AppSetting(key=key, value=value))

    await db.commit()

    # Apply vào settings singleton ngay lập tức
    settings.update(**updates)

    # Trả về config mới nhất (masked)
    return LLMConfigResponse(
        llm_mode=settings.llm_mode,
        llm_api_key=_mask_key(settings.llm_api_key),
        llm_base_url=settings.llm_base_url,
        llm_model=settings.llm_model,
        updated_at=datetime.utcnow().isoformat(),
    )
