from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.deal import DealRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.deal_repo = DealRepository(session)
        self._cache: dict[str, tuple[datetime, Any]] = {}
        self._cache_ttl = timedelta(minutes=5)

    def _get_cache_key(self, organization_id: UUID, method: str) -> str:
        return f"{method}:{organization_id}"

    def _get_from_cache(self, key: str) -> Any | None:
        if key in self._cache:
            timestamp, value = self._cache[key]
            if datetime.now() - timestamp < self._cache_ttl:
                return value
            del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        self._cache[key] = (datetime.now(), value)

    async def get_deals_summary(self, organization_id: UUID) -> dict[str, int | Decimal]:
        cache_key = self._get_cache_key(organization_id, "summary")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        summary = await self.deal_repo.get_summary(organization_id)
        self._set_cache(cache_key, summary)
        return summary

    async def get_deals_funnel(self, organization_id: UUID) -> list[dict[str, int | str]]:
        cache_key = self._get_cache_key(organization_id, "funnel")
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        funnel = await self.deal_repo.get_funnel(organization_id)
        self._set_cache(cache_key, funnel)
        return funnel
