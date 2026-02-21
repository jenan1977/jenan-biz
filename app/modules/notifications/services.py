"""Notifications service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification, NotificationType


class NotificationsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        company_id: uuid.UUID | None = None,
        link: str | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            company_id=company_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def get_unread(self, user_id: uuid.UUID) -> List[Notification]:
        res = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            ).order_by(Notification.created_at.desc())
        )
        return list(res.scalars().all())

    async def mark_read(self, notification_id: uuid.UUID) -> None:
        res = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = res.scalar_one_or_none()
        if notification:
            notification.is_read = True
            await self.db.flush()
