PRICING_TIERS = {
    "essential": {
        "name": "Essential",
        "monthly_price": 2.99,
        "annual_price": 29.99,
        "monthly_quota": 5,
        "daily_limit": 2,
        "models": ["Gemini 2.5 Pro", "DeepSeek V3.2", "Grok 4.1 Fast", "GPT-5 Mini"]
    },
    "plus": {
        "name": "Plus",
        "monthly_price": 5.99,
        "annual_price": 59.99,
        "monthly_quota": 12,
        "daily_limit": 4,
        "models": ["MoonshotAI Kimi K2.5", "Gemini 3 Flash Preview", "Gemini 3 Pro Preview", "Qwen3.5-35B-A3B"]
    },
    "premium": {
        "name": "Premium",
        "monthly_price": 11.99,
        "annual_price": 119.99,
        "monthly_quota": 25,
        "daily_limit": 10,
        "models": ["Gemini 3.1 Flash Lite Preview", "Gemini 3.1 Pro Preview", "Claude Opus 4.5", "Claude Haiku 4.5"]
    },
    "ultimate": {
        "name": "Ultimate",
        "monthly_price": 19.99,
        "annual_price": 199.99,
        "monthly_quota": 50,
        "daily_limit": 15,
        "models": ["Z.ai GLM 5", "OpenAI GPT-5.4", "Claude Sonnet 4.6", "Claude Opus 4.6"]
    }
}

BOOSTER_PACKS = {
    "single": {"name": "1 Booster", "analyses": 10, "price": 0.99},
    "multipack_10": {"name": "10 Booster", "analyses": 100, "price": 8.99, "discount": 0.1},
    "multipack_50": {"name": "50 Booster", "analyses": 500, "price": 39.99, "discount": 0.2}
}

LEVELING_SYSTEM = {
    "xp_gain": {
        "analysis": 1,
        "profit_signal": 5,
        "share_signal": 2,
        "referral": 10,
        "daily_login": 1
    },
    "tiers": [
        {"range": (1, 5), "xp": 50, "benefits": "Akses dasar"},
        {"range": (6, 10), "xp": 200, "benefits": "+1 daily analysis, 5% booster discount"},
        {"range": (11, 15), "xp": 500, "benefits": "+2 daily analysis, 10% booster discount"},
        {"range": (16, 20), "xp": 1000, "benefits": "Priority queue, 15% booster discount"},
        {"range": (21, 25), "xp": 2000, "benefits": "+5 daily analysis, Exclusive model access"},
        {"range": (26, 999), "xp": 999999, "benefits": "Custom badge, 20% booster discount"}
    ]
}
