import datetime
import subprocess
import pytz

# Configuration
WIB = pytz.timezone("Asia/Jakarta")
MT5_CONTAINER = "mt5-exness"

def is_market_open():
    """
    Checks if the Forex market is open based on WIB time.
    Monday 05:00 WIB to Saturday 05:00 WIB.
    """
    now = datetime.datetime.now(WIB)
    weekday = now.weekday() # 0=Monday, 5=Saturday, 6=Sunday
    hour = now.hour

    # Monday start (05:00)
    if weekday == 0:
        return hour >= 5
    
    # Tuesday to Friday
    if 1 <= weekday <= 4:
        return True
    
    # Saturday end (05:00)
    if weekday == 5:
        return hour < 5
    
    # Sunday CLOSED
    if weekday == 6:
        return False

    return False

def control_mt5():
    open_status = is_market_open()
    print(f"[{datetime.datetime.now(WIB)}] Market Open: {open_status}")

    try:
        if open_status:
            print(f"Ensuring {MT5_CONTAINER} is running...")
            subprocess.run(["docker", "start", MT5_CONTAINER], check=True)
        else:
            print(f"Market Closed. Stopping {MT5_CONTAINER} to save resources...")
            subprocess.run(["docker", "stop", MT5_CONTAINER], check=True)
    except Exception as e:
        print(f"Error controlling MT5: {e}")

if __name__ == "__main__":
    control_mt5()
