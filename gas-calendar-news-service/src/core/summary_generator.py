"""Generate text summaries from calendar events."""
def generate_event_summary(events: list[dict]) -> str:
    if not events: return "No economic events in the specified period."
    lines = []
    for e in events:
        actual = e.get("actual_value","N/A")
        forecast = e.get("forecast_value","N/A")
        previous = e.get("previous_value","N/A")
        lines.append(f"- {e['country']}: {e['title']} ({e['importance']}) actual {actual}, forecast {forecast}, previous {previous}")
    header = f"Economic Events Summary ({len(events)} events):"
    return header + "\n" + "\n".join(lines)
