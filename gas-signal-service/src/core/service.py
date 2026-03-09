from src.db.repositories.signal_repo import SignalRepository
from src.redis.client import redis_client
from src.core.billing_client import billing_client
from uuid import UUID

class SignalCoreService:
    def __init__(self, repo: SignalRepository):
        self.repo = repo

    async def create_new_signal(self, data: dict):
        # Determine source correctly
        signal = await self.repo.create_signal(
            tier=data['tier'],
            source=data.get('source', 'unknown'),
            symbol=data['symbol'],
            timeframe=data.get('timeframe'),
            action=data['action'],
            entry_price=data['entry_price'],
            stop_loss=data['stop_loss'],
            take_profit=data['take_profit'],
            confidence=data.get('confidence'),
            metadata_info=data.get('metadata_info')
        )
        
        # Prepare for redis
        sig_data = {
            "id": str(signal.id),
            "tier": signal.tier.value,
            "symbol": signal.symbol,
            "action": signal.action.value,
            "entry_price": signal.entry_price,
            "source": signal.source
        }
        await redis_client.publish_signal(f"signals:new:{signal.tier.value}", sig_data)
        return signal

    async def get_signals_for_user(self, user_id: str, user_token: str, filters: dict):
        # 1. Ask billing service for accessible tiers
        allowed_tiers = await billing_client.get_user_allowed_tiers(user_id, user_token)
        
        # User requested specific tiers via filters
        requested_tiers = filters.get('tier')
        if requested_tiers:
            req_list = [t.strip() for t in requested_tiers.split(',')]
            # intersection
            allowed_tiers = [t for t in req_list if t in allowed_tiers]
            
        signals, total = await self.repo.get_signals(
            allowed_tiers=allowed_tiers,
            symbol=filters.get('symbol'),
            limit=filters.get('limit', 50),
            offset=filters.get('offset', 0)
        )
        return signals, total
        
    async def expire(self, signal_id: UUID):
        return await self.repo.expire_signal(signal_id)
        
    async def delete_signal(self, signal_id: UUID):
        return await self.repo.delete_signal(signal_id)
