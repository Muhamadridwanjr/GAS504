import os
import time
import subprocess
import datetime
import requests
import json
import sqlite3
from typing import List, Dict

# Configuration
DB_PATH = "/var/lib/postgresql/data" # This is a placeholder, we need to find the actual mapped host path or use docker exec
DOCKER_NETWORK = "gas-network"
CALENDAR_SERVICE_URL = "http://gas-calendar-news-service:9601/calendar" # Internal URL
POSTGRES_HOST = "gas-user-db"
MANAGEMENT_SCRIPT = "/root/gasstrategyai/scripts/automation_manager.sh"

def get_upcoming_high_impact_events():
    """
    Query the news service or DB for upcoming High Impact events.
    We'll use the API if possible as it's cleaner.
    """
    try:
        # Check next 30 minutes
        now = datetime.datetime.utcnow()
        end = now + datetime.timedelta(minutes=30)
        
        # Since we are running on the host, we can't easily hit the container inner URL
        # unless we use the mapped port or docker exec. 
        # For simplicity and robustness, we use 'docker exec' to query the DB directly.
        
        cmd = [
            "docker", "exec", "gas-user-db", 
            "psql", "-U", "postgres", "-d", "gas_calendar", "-c",
            f"SELECT count(*) FROM economic_events WHERE importance = 'high' AND time_utc BETWEEN '{now.isoformat()}' AND '{end.isoformat()}';"
        ]
        
        result = subprocess.check_output(cmd).decode('utf-8')
        # Parse the psql output (usually count is in the 3rd line)
        lines = result.strip().split('\n')
        for line in lines:
            if line.strip().isdigit():
                return int(line.strip()) > 0
        return False
    except Exception as e:
        print(f"Error checking news: {e}")
        return False

def main():
    print(f"[{datetime.datetime.now()}] Checking for high-impact news...")
    if get_upcoming_high_impact_events():
        print("High impact news found! Triggering wake-up...")
        subprocess.run([MANAGEMENT_SCRIPT, "NEWS_PULSE"])
    else:
        print("No high impact news in the immediate horizon.")

if __name__ == "__main__":
    main()
