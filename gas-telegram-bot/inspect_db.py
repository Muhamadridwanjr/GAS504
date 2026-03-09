import httpx
import json

SUPABASE_URL = "https://psiadtkmrxwxiknrstdf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzaWFkdGttcnh3eGlrbnJzdGRmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTM4NzM4NywiZXhwIjoyMDg2OTYzMzg3fQ.6Tm9pNbqS2C2hZsLKfkicIWsR5k-NZdtTO2Nvnr7H_U"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def check_tables():
    url = f"{SUPABASE_URL}/rest/v1/?apikey={SUPABASE_KEY}"
    try:
        r = httpx.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            paths = list(data.get("paths", {}).keys())
            tables = set()
            for p in paths:
                if p.startswith('/'):
                    tbl = p.split('/')[1]
                    tables.add(tbl)
            print("Tables found:", tables)
            
            for t in ["users", "profiles", "user_profiles", "user_service"]:
                if f"/{t}" in paths:
                    print(f"Schema for {t}:")
                    print(json.dumps(data["definitions"].get(t, {}).get("properties", {}), indent=2))
        else:
            print(f"Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_tables()
