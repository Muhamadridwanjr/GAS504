from fastapi import APIRouter, HTTPException, Request
import json
from src.models.tick import TickBatch
from src.models.ohlc import OHLCData
from src.models.heartbeat import HeartbeatData
from src.models.account_heartbeat import AccountHeartbeatData
from src.redis_client.client import redis_client
from src.lib.logger import log

router = APIRouter()

# ──────────────────────────────────────────────────────────
# MULTI-SYMBOL SCANNER ENDPOINTS
# Receives batch data from GAS Scanner EA (all pairs at once)
# ──────────────────────────────────────────────────────────

@router.post("/multitick")
@router.post("/multitick/")
async def receive_multitick(request: Request):
    """
    Batch tick snapshot for ALL scanner symbols.
    Payload: {"scanner_id":"...", "symbols":[{"symbol":"EURUSD","bid":1.085,"ask":1.086,"spread":1,"time":123,"category":"Forex"}, ...]}
    """
    body = await request.body()
    try:
        data = json.loads(body)
        symbols = data.get("symbols", [])
    except Exception as e:
        log.error(f"Validation Error /multitick: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    if not symbols:
        return {"status": "ok", "count": 0}

    try:
        pipe = redis_client.client.pipeline()
        for s in symbols:
            sym = s.get("symbol", "")
            if not sym:
                continue
            # Store latest snapshot per symbol (TTL 60s)
            pipe.set(f"market:{sym}", json.dumps(s), ex=60)
            # Keep a sorted list of last 10 tick snapshots for charting
            pipe.lpush(f"ticks_snap:{sym}", json.dumps(s))
            pipe.ltrim(f"ticks_snap:{sym}", 0, 9)
        await pipe.execute()

        # Publish single event for realtime hub
        await redis_client.client.publish("market:scanner", json.dumps({
            "scanner_id": data.get("scanner_id", ""),
            "count": len(symbols),
            "symbols": [s.get("symbol") for s in symbols],
        }))

        log.info(f"Scanner snapshot: {len(symbols)} symbols")
        return {"status": "ok", "count": len(symbols)}
    except Exception as e:
        log.error(f"Error processing multitick: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multiohlc")
@router.post("/multiohlc/")
async def receive_multiohlc(request: Request):
    """
    Batch OHLCV for ALL scanner symbols in one timeframe.
    Payload: {"timeframe":"M15", "bars":[{"symbol":"EURUSD","time":123,"open":1.085,"high":1.090,"low":1.082,"close":1.087,"volume":12345}, ...]}
    """
    body = await request.body()
    try:
        data = json.loads(body)
        timeframe = data.get("timeframe", "M15")
        bars = data.get("bars", [])
    except Exception as e:
        log.error(f"Validation Error /multiohlc: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    if not bars:
        return {"status": "ok", "count": 0}

    try:
        pipe = redis_client.client.pipeline()
        for bar in bars:
            sym = bar.get("symbol", "")
            if not sym:
                continue
            key = f"ohlc:{sym}:{timeframe}"
            pipe.lpush(key, json.dumps(bar))
            pipe.ltrim(key, 0, 499)  # keep last 500 bars per symbol/tf
        await pipe.execute()

        # Publish for realtime subscribers
        await redis_client.client.publish(f"market:ohlc:{timeframe}", json.dumps({
            "timeframe": timeframe,
            "count": len(bars),
        }))

        log.info(f"MultiOHLC {timeframe}: {len(bars)} bars")
        return {"status": "ok", "timeframe": timeframe, "count": len(bars)}
    except Exception as e:
        log.error(f"Error processing multiohlc: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tick")
@router.post("/tick/")
async def receive_tick(request: Request):
    body = await request.body()
    try:
        data = json.loads(body)
        batch = TickBatch(**data)
    except Exception as e:
        log.error(f"Validation Error /tick: {e} | Body: {body.decode(errors='ignore')}")
        raise HTTPException(status_code=422, detail=str(e))

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
    """EA Utama heartbeat — stores globally keyed by symbol."""
    log.info(f"Received Heartbeat from EA - Symbol: {data.symbol}")
    try:
        key = f"heartbeat:{data.symbol}"
        await redis_client.client.set(key, json.dumps(data.model_dump()), ex=120)  # Expire in 2 mins
        
        await redis_client.client.publish("system:heartbeat", data.model_dump_json())
        return {"status": "ok"}
    except Exception as e:
        log.error(f"Error processing heartbeat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/account-heartbeat")
@router.post("/account-heartbeat/")
async def receive_account_heartbeat(request: Request):
    """
    Per-user EA account heartbeat.
    """
    body = await request.body()
    try:
        data_dict = json.loads(body)
        data = AccountHeartbeatData(**data_dict)
    except Exception as e:
        log.error(f"Validation Error /account-heartbeat: {e} | Body: {body.decode(errors='ignore')}")
        raise HTTPException(status_code=422, detail=str(e))

    user_id = data.user_id.strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    log.info(f"Received AccountHeartbeat from EA - user_id={user_id} account={data.account_id}")
    try:
        # Calculate floating PnL if not provided
        floating_pnl = data.floating_pnl or (data.equity - data.balance)

        # Store account summary
        account_summary = {
            "user_id": user_id,
            "account_id": data.account_id,
            "broker": data.broker,
            "server": data.server,
            "currency": data.currency,
            "leverage": data.leverage,
            "balance": data.balance,
            "equity": data.equity,
            "margin": data.margin,
            "free_margin": data.free_margin,
            "margin_level": data.margin_level,
            "floating_pnl": floating_pnl,
            "daily_pnl": data.daily_pnl,
            "positions_count": len(data.positions) if data.positions else data.positions_count,
            "ea_version": data.ea_version,
            "symbol": data.symbol,
            "last_update": __import__('datetime').datetime.utcnow().isoformat(),
        }
        
        key_account = f"account:{user_id}"
        key_positions = f"account:{user_id}:positions"
        
        # Store account data (TTL 5 min — if EA stops, data expires)
        await redis_client.client.set(key_account, json.dumps(account_summary), ex=300)
        
        # Store positions list
        positions_data = [p.model_dump() for p in data.positions] if data.positions else []
        await redis_client.client.set(key_positions, json.dumps(positions_data), ex=300)
        
        # Publish event for realtime hub
        await redis_client.client.publish(
            f"account:{user_id}:update",
            json.dumps(account_summary)
        )
        
        return {
            "status": "ok",
            "user_id": user_id,
            "positions_received": len(positions_data)
        }
    except Exception as e:
        log.error(f"Error processing account heartbeat for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
