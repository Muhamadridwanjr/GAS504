from fastapi import APIRouter, HTTPException
import json
from src.models.tick import TickBatch
from src.models.ohlc import OHLCData
from src.models.heartbeat import HeartbeatData
from src.redis_client.client import redis_client
from src.lib.logger import log

router = APIRouter()

@router.post("/tick")
@router.post("/tick/")
async def receive_tick(batch: TickBatch):
    log.info(f"Received tick for {batch.symbol} - count: {len(batch.ticks)}")
    try:
        key = f"ticks:{batch.symbol}"
        for tick in batch.ticks:
            await redis_client.client.lpush(key, json.dumps(tick.model_dump()))
            await redis_client.client.ltrim(key, 0, 999)
        
        await redis_client.client.publish("market:ticks", batch.model_dump_json())
        return {"status": "ok", "count": len(batch.ticks)}
    except Exception as e:
        log.error(f"Error processing ticks for {batch.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ohlc")
@router.post("/ohlc/")
async def receive_ohlc(data: OHLCData):
    log.info(f"Received OHLC for {data.symbol} - TF: {data.timeframe}")
    try:
        key = f"ohlc:{data.symbol}:{data.timeframe}"
        await redis_client.client.lpush(key, json.dumps(data.model_dump()))
        await redis_client.client.ltrim(key, 0, 999)
        
        await redis_client.client.publish(f"market:ohlc:{data.symbol}", data.model_dump_json())
        return {"status": "ok"}
    except Exception as e:
        log.error(f"Error processing OHLC for {data.symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/heartbeat")
@router.post("/heartbeat/")
async def receive_heartbeat(data: HeartbeatData):
    log.info(f"Received Heartbeat from EA - Symbol: {data.symbol}")
    try:
        key = f"heartbeat:{data.symbol}"
        await redis_client.client.set(key, json.dumps(data.model_dump()), ex=120)  # Expire in 2 mins
        
        await redis_client.client.publish("system:heartbeat", data.model_dump_json())
        return {"status": "ok"}
    except Exception as e:
        log.error(f"Error processing heartbeat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
