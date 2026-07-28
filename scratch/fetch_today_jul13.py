import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

acts = client.get_activities_by_date("2026-07-13", "2026-07-13")
print(f"Activities on 2026-07-13: {len(acts)} found\n")
for a in acts:
    sport = a.get("activityType", {}).get("typeKey", "unknown")
    name = a.get("activityName", "N/A")
    dur = (a.get("duration", 0) or 0) / 60
    dist = (a.get("distance", 0) or 0) / 1000
    avg_hr = a.get("averageHR", 0) or 0
    max_hr = a.get("maxHR", 0) or 0
    aer_te = a.get("aerobicTrainingEffect", 0) or 0
    kcal = a.get("calories", 0) or 0
    print(f"[{sport.upper()}] {name}")
    print(f"  Distance: {dist:.2f} km | Duration: {dur:.1f} min")
    print(f"  Avg HR: {avg_hr:.0f} bpm | Max HR: {max_hr:.0f} bpm")
    print(f"  Aer TE: {aer_te:.1f} | Calories: {kcal:.0f} kcal")
    print()
