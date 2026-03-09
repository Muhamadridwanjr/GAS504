from fastapi import APIRouter

router = APIRouter(tags=["Public Landing Page"])

@router.get("/stats")
async def get_public_stats():
    # Will fetch from user and signal service
    return {
        "total_users": 15000,
        "total_analysis": 100000,
        "active_signals": 15
    }

@router.get("/market-pulse")
async def get_market_pulse():
    return {
        "sentiment": "BULLISH",
        "description": "Global market is showing strong upward momentum."
    }

@router.get("/top-signals")
async def get_top_signals():
    return [
        {"pair": "XAUUSD", "performance": "+150 pips"},
        {"pair": "EURUSD", "performance": "+50 pips"}
    ]

@router.get("/testimonials")
async def get_testimonials():
    return [
        {"user": "John D.", "text": "GAS is amazing for my trading!"},
        {"user": "Sarah L.", "text": "The AI analysis is top notch."}
    ]
