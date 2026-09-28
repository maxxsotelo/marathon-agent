import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
from garminconnect import Garmin
import json

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

print("Fetching all activities from July 1, 2026 to September 28, 2026...")
activities = client.get_activities(0, 100) # Fetch recent 100 activities

runs = []
for act in activities:
    act_date = act.get("startTimeLocal", "")[:10]
    act_type = act.get("activityType", {}).get("typeKey", "")
    dist_km = act.get("distance", 0) / 1000.0
    name = act.get("activityName", "")
    duration_m = act.get("duration", 0) / 60.0
    
    if "running" in act_type or "cycling" in act_type or dist_km > 1.0:
        runs.append({
            "date": act_date,
            "name": name,
            "type": act_type,
            "distance_km": round(dist_km, 2),
            "duration_min": round(duration_m, 1),
            "id": act.get("activityId")
        })

print(f"Total matching activities found: {len(runs)}")
print("\n--- ALL RUNS & ACTIVITIES LOGGED ---")
for r in sorted(runs, key=lambda x: x["date"], reverse=True):
    print(f"[{r['date']}] {r['type'].upper()} | {r['distance_km']} km | {r['duration_min']} mins | '{r['name']}' (ID: {r['id']})")
