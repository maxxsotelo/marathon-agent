import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

acts = client.get_activities_by_date("2026-07-08", "2026-07-14")
print("=== Last 7 Days Activity Summary ===\n")
total_run_km = 0
for a in acts:
    sport = a.get("activityType", {}).get("typeKey", "unknown")
    name = a.get("activityName", "N/A")
    dur = (a.get("duration", 0) or 0) / 60
    dist = (a.get("distance", 0) or 0) / 1000
    aer_te = a.get("aerobicTrainingEffect", 0) or 0
    kcal = a.get("calories", 0) or 0
    start = a.get("startTimeLocal", "")[:10]
    print(f"[{start}] {sport.upper():<22} | {dist:.2f} km | {dur:.0f} min | TE: {aer_te:.1f} | {kcal:.0f} kcal")
    if "running" in sport:
        total_run_km += dist

print(f"\nTotal running km (last 7 days): {total_run_km:.2f} km")
