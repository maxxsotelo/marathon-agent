import os
from datetime import date, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA: "),
)
client.login(TOKEN_STORE)

# Pull up to 200 running activities to check all HM+ runs
acts = client.get_activities(0, 200)

hm_runs = []
longest_run = 0.0

for a in acts:
    t = a.get("activityType", {}).get("typeKey", "?")
    if "running" in t:
        dist_km = (a.get("distance") or 0) / 1000
        dur_min = (a.get("duration") or 0) / 60
        if dist_km > longest_run:
            longest_run = dist_km
        if dist_km >= 21.0:
            hm_runs.append({
                "date": a.get("startTimeLocal", "")[:10],
                "name": a.get("activityName"),
                "dist": dist_km,
                "dur": dur_min,
                "pace": a.get("averageSpeed"),
                "ahr": a.get("averageHR"),
                "te": a.get("aerobicTrainingEffect")
            })

print(f"Total Half Marathon distance runs (>= 21.0 km) in recent history: {len(hm_runs)}")
print(f"Longest run found in fetched activities: {longest_run:.2f} km")
print("\nList of HM+ runs:")
for r in sorted(hm_runs, key=lambda x: x["date"]):
    speed = r["pace"]
    p_str = "-"
    if speed and speed > 0:
        s = 1000 / speed
        p_str = f"{int(s//60)}:{int(s%60):02d}/km"
    print(f"  {r['date']} | {r['dist']:5.2f} km | {r['dur']:4.0f} min ({p_str}) | HR: {r['ahr']} | TE: {r['te']} | {r['name']}")
