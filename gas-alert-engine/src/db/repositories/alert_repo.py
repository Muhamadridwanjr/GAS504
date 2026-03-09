from uuid import UUID
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Alert, AlertHistory
from src.lib.logger import logger


class AlertRepository:
    """Data-access layer for Alert and AlertHistory."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Create ───────────────────────────────────────────────
    async def create(self, data: dict) -> Alert:
        alert = Alert(**data)
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        logger.info(f"Alert {alert.id} created for user {alert.user_id}")
        return alert

    # ── Read ─────────────────────────────────────────────────
    async def get_by_id(self, alert_id: UUID) -> Optional[Alert]:
        result = await self.session.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: UUID,
        active: Optional[bool] = None,
        symbol: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Alert], int]:
        query = select(Alert).where(Alert.user_id == user_id)
        count_query = select(func.count()).select_from(Alert).where(Alert.user_id == user_id)

        if active is not None:
            query = query.where(Alert.active == active)
            count_query = count_query.where(Alert.active == active)
        if symbol:
            query = query.where(Alert.symbol == symbol)
            count_query = count_query.where(Alert.symbol == symbol)

        query = query.order_by(Alert.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        count_result = await self.session.execute(count_query)

        return list(result.scalars().all()), count_result.scalar_one()

    async def get_active_by_symbol_timeframe(
        self, symbol: str, timeframe: Optional[str] = None
    ) -> list[Alert]:
        """Get all active alerts for a given symbol (and optional timeframe)."""
        query = select(Alert).where(
            Alert.active == True,
            Alert.symbol == symbol,
        )
        if timeframe:
            query = query.where(Alert.timeframe == timeframe)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ── Update ───────────────────────────────────────────────
    async def update_alert(self, alert_id: UUID, data: dict) -> Optional[Alert]:
        alert = await self.get_by_id(alert_id)
        if not alert:
            return None
        for key, value in data.items():
            if hasattr(alert, key) and value is not None:
                setattr(alert, key, value)
        alert.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def set_active(self, alert_id: UUID, active: bool) -> Optional[Alert]:
        return await self.update_alert(alert_id, {"active": active})

    async def record_trigger(self, alert_id: UUID, trigger_data: dict | None = None) -> None:
        """Update last_triggered and write history row."""
        now = datetime.now(timezone.utc)
        await self.session.execute(
            update(Alert)
            .where(Alert.id == alert_id)
            .values(last_triggered=now, updated_at=now)
        )
        history = AlertHistory(
            alert_id=alert_id,
            triggered_at=now,
            trigger_data=trigger_data,
        )
        self.session.add(history)
        await self.session.commit()
        logger.info(f"Alert {alert_id} triggered, history recorded")

    # ── Delete (soft) ────────────────────────────────────────
    async def soft_delete(self, alert_id: UUID) -> bool:
        alert = await self.get_by_id(alert_id)
        if not alert:
            return False
        alert.active = False
        alert.updated_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True

    # ── History ──────────────────────────────────────────────
    async def get_history(self, alert_id: UUID, limit: int = 20) -> list[AlertHistory]:
        result = await self.session.execute(
            select(AlertHistory)
            .where(AlertHistory.alert_id == alert_id)
            .order_by(AlertHistory.triggered_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
