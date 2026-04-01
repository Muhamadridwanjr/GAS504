"""
GAS Bot — Credit Service
Atomic credit operations via Redis WATCH + pipeline.
Redis key: user:{gas_user_id}:credits  (integer string)
"""
from src.services.redis_client import get_redis
from src.utils.logger import logger


async def deduct(gas_user_id: str, cost: int) -> tuple[bool, int]:
    """
    Atomically deduct `cost` credits.
    Returns (success, remaining_balance).
    Retries up to 3 times on WATCH conflict.
    """
    r = await get_redis()
    key = f"user:{gas_user_id}:credits"

    for attempt in range(3):
        try:
            async with r.pipeline(transaction=True) as pipe:
                await pipe.watch(key)
                raw     = await pipe.get(key)
                balance = int(raw or 0)
                if balance < cost:
                    await pipe.unwatch()
                    return False, balance
                pipe.multi()
                pipe.decrby(key, cost)
                results   = await pipe.execute()
                remaining = int(results[0])
                logger.info("credits_deducted", user=gas_user_id, cost=cost, remaining=remaining)
                return True, remaining
        except Exception as e:
            logger.warning("credit_deduct_retry", attempt=attempt, error=str(e))

    return False, 0


async def refund(gas_user_id: str, cost: int) -> int:
    """Refund credits (called when a worker job fails). Returns new balance."""
    r    = await get_redis()
    new  = await r.incrby(f"user:{gas_user_id}:credits", cost)
    logger.info("credits_refunded", user=gas_user_id, amount=cost, balance=new)
    return int(new)


async def get_balance(gas_user_id: str) -> int:
    r   = await get_redis()
    raw = await r.get(f"user:{gas_user_id}:credits")
    return int(raw or 0)
