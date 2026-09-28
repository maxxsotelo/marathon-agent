import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

print("Fetching ALL historical activities...")
all_activities = []
start = 0
limit = 100
while True:
    acts = client.get_activities(start, limit)
    if not acts:
        break
    all_activities.extend(acts)
    if len(acts) < limit:
        break
    start += limit
    if start >= 500: # safety cap
        break

print(f"Total total activities fetched: {len(all_activities)}")
long_runs = []
for a in all_activities:
    d_km = a.get("distance", 0) / 1000.0
    if d_km >= 18.0:
        long_runs.append({
            "date": a.get("startTimeLocal", "")[:10],
            "name": a.get("activityName", ""),
            "distance_km": round(d_km, 2),
            "duration_min": round(a.get("duration", 0)/60.0, 1),
            "type": a.get("activityType", {}).get("typeKey", "")
        })

print("\n=== ALL HISTORICAL RUNS >= 18 KM IN GARMIN ===")
for r in sorted(long_runs, key=lambda x: x["date"], reverse=True):
    print(f"[{r['date']}] {r['type']} | {r['distance_km']} km | {r['duration_min']} mins | '{r['name']}'")
