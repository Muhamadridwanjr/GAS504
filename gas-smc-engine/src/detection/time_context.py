"""
Time Context Filter — Real SMC Implementation
Detects: Active Kill Zones (Asia/London/NY), AMD Cycle phase, Day-of-week context
"""
from datetime import datetime, timezone
from typing import List, Dict, Any

# Kill zone definitions in UTC hours (start inclusive, end exclusive)
KILL_ZONES = {
    "asia":         {"start": 0,  "end": 4,  "label": "Asia Session",          "description": "00:00–04:00 UTC — low volatility, range building"},
    "london_open":  {"start": 7,  "end": 10, "label": "London Open",           "description": "07:00–10:00 UTC — HIGH volatility, institutional moves"},
    "ny_open":      {"start": 13, "end": 16, "label": "New York Open",         "description": "13:00–16:00 UTC — HIGH volatility, peak liquidity"},
    "london_close": {"start": 15, "end": 17, "label": "London/NY Overlap",     "description": "15:00–17:00 UTC — peak session overlap, large moves"},
}

# AMD Cycle phases by UTC hour
def _get_amd_phase(hour: int) -> Dict[str, str]:
    if 0 <= hour < 4:
        return {
            "phase":       "ACCUMULATION",
            "description": "Asia session — smart money quietly building positions in a range",
            "advice":      "Avoid trading, observe range boundaries for inducement setups",
        }
    elif 4 <= hour < 8:
        return {
            "phase":       "MANIPULATION",
            "description": "Pre-London — watch for fake breakouts and stop hunts before real move",
            "advice":      "High-probability: look for liquidity sweeps that reverse into kill zone",
        }
    elif 8 <= hour < 12:
        return {
            "phase":       "DISTRIBUTION",
            "description": "London session — smart money distributing/offloading, high directional moves",
            "advice":      "Best time for SMC entries after London stop hunt. Trade with institutional bias.",
        }
    elif 12 <= hour < 17:
        return {
            "phase":       "DISTRIBUTION",
            "description": "NY session — continuation or reversal of London move, peak volume",
            "advice":      "Look for NY continuation trades or NY reversal after London distribution.",
        }
    elif 17 <= hour < 20:
        return {
            "phase":       "RE-ACCUMULATION",
            "description": "Post-NY — market digesting moves, consolidation before next session",
            "advice":      "Reduce size, tighten targets. Avoid chasing extended moves.",
        }
    else:
        return {
            "phase":       "ACCUMULATION",
            "description": "Late/overnight session — low liquidity, choppy price action",
            "advice":      "Stand aside. Wait for Asia or London open to define direction.",
        }


class TimeContextFilter:
    def detect(self, candles: list = None, params: dict = None) -> Dict[str, Any]:
        now   = datetime.now(timezone.utc)
        hour  = now.hour
        wday  = now.weekday()          # 0=Mon, 4=Fri, 5=Sat, 6=Sun
        wname = now.strftime("%A")

        # ── Active Kill Zones ──────────────────────────────────────────────────
        active_zones = []
        for kz_name, kz in KILL_ZONES.items():
            if kz["start"] <= hour < kz["end"]:
                active_zones.append({
                    "name":        kz_name.upper(),
                    "label":       kz["label"],
                    "description": kz["description"],
                })

        in_kill_zone = len(active_zones) > 0

        # ── AMD Phase ─────────────────────────────────────────────────────────
        amd = _get_amd_phase(hour)

        # ── Day-of-Week Context ───────────────────────────────────────────────
        day_note = None
        if wday == 0 and hour < 8:                          # Monday pre-London
            day_note = "Monday open — wait for liquidity to establish weekly direction before entering"
        elif wday == 2:                                     # Wednesday
            day_note = "Mid-week — highest liquidity day, best SMC setups tend to form"
        elif wday == 3 and hour >= 18:                      # Thursday late
            day_note = "Thursday late — institutions starting to book profits heading into Friday"
        elif wday == 4 and hour >= 17:                      # Friday close
            day_note = "Friday close — AVOID new positions, risk of gap on Monday. Close trades."
        elif wday in (5, 6):                                # Weekend
            day_note = "Weekend — markets closed or very low liquidity (crypto only). No new setups."

        # ── Best sessions for SMC ─────────────────────────────────────────────
        # High-probability SMC windows: London Open + NY Open
        is_high_prob_window = (7 <= hour < 10) or (13 <= hour < 16)

        # ── Session label ─────────────────────────────────────────────────────
        if 0 <= hour < 7:
            session_label = "Asia"
        elif 7 <= hour < 13:
            session_label = "London"
        elif 13 <= hour < 20:
            session_label = "New York"
        else:
            session_label = "Off-hours"

        return {
            "current_utc":         now.strftime("%Y-%m-%d %H:%M UTC"),
            "current_hour_utc":    hour,
            "weekday":             wname,
            "session":             session_label,
            "active_kill_zones":   active_zones,
            "in_kill_zone":        in_kill_zone,
            "is_high_prob_window": is_high_prob_window,
            "amd_phase":           amd["phase"],
            "amd_description":     amd["description"],
            "amd_advice":          amd["advice"],
            "day_note":            day_note,
            "trading_recommendation": (
                "ACTIVE" if in_kill_zone and wday < 5
                else "STANDBY" if not in_kill_zone and wday < 5
                else "CLOSED"
            ),
        }
