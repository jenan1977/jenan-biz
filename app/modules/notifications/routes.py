"""Notifications routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.notifications.services import NotificationsService
    return await NotificationsService(db).get_unread(current_user.id)


@router.put("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    from app.modules.notifications.services import NotificationsService
    await NotificationsService(db).mark_read(notification_id)
