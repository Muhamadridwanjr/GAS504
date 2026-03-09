from datetime import datetime, timedelta
from src.core.pricing_data import PRICING_TIERS, LEVELING_SYSTEM

def can_perform_analysis(user_credits):
    # 1. Check Daily Reset
    now = datetime.utcnow()
    if user_credits.last_reset_date.date() < now.date():
        user_credits.daily_usage = 0
        user_credits.last_reset_date = now

    # 2. Check Tier Limits
    tier_config = PRICING_TIERS.get(user_credits.tier.lower())
    if not tier_config:
        return False, "No active subscription"

    daily_limit = tier_config["daily_limit"]
    
    # Check if level adds daily bonus
    if 6 <= user_credits.level <= 10:
        daily_limit += 1
    elif 11 <= user_credits.level <= 15:
        daily_limit += 2
    elif 21 <= user_credits.level <= 25:
        daily_limit += 5

    if user_credits.daily_usage >= daily_limit:
        return False, "Daily limit reached"

    # 3. Check Quota/Boost
    if user_credits.quota > 0:
        return True, "quota"
    elif user_credits.boost > 0:
        return True, "boost"
    
    return False, "Monthly quota exhausted"

def consume_analysis(user_credits, credit_type):
    if credit_type == "quota":
        user_credits.quota -= 1
    elif credit_type == "boost":
        user_credits.boost -= 1
    
    user_credits.daily_usage += 1
    add_xp(user_credits, LEVELING_SYSTEM["xp_gain"]["analysis"])

def add_xp(user_credits, amount):
    user_credits.level_score += amount
    
    # Simple leveling logic based on thresholds
    current_level = user_credits.level
    new_level = current_level
    
    for tier in LEVELING_SYSTEM["tiers"]:
        if user_credits.level_score >= tier["xp"]:
             # If score is above the threshold for this tier, 
             # the max level for this tier is the upper range
             new_level = max(new_level, tier["range"][1])
        else:
            # We found the target tier
            # Level within tier = current_tier_start + (remaining_xp / (xp_to_next_tier / levels_in_tier))
            # For simplicity, let's just use the tier thresholds as level milestones
            break
    
    # Re-evaluating leveling to match:
    # 1-5: 0-50 XP
    # 6-10: 51-200 XP
    # 11-15: 201-500 XP
    # etc.
    
    if user_credits.level_score <= 50:
        new_level = 1 + (user_credits.level_score // 10) # Level 1-5
    elif user_credits.level_score <= 200:
        new_level = 6 + ((user_credits.level_score - 51) // 30) # Level 6-10
    elif user_credits.level_score <= 500:
        new_level = 11 + ((user_credits.level_score - 201) // 60) # Level 11-15
    elif user_credits.level_score <= 1000:
        new_level = 16 + ((user_credits.level_score - 501) // 100) # Level 16-20
    elif user_credits.level_score <= 2000:
        new_level = 21 + ((user_credits.level_score - 1001) // 200) # Level 21-25
    else:
        new_level = 26 + ((user_credits.level_score - 2001) // 500) # Level 26+

    user_credits.level = min(new_level, 99) # Cap level for UI
