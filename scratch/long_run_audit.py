import os, sys
from datetime import date, timedelta
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Pull all long runs (21km+) from activity history
page = 0
all_runs = []
while True:
    acts = client.get_activities(page, 100)
    if not acts:
        break
    for a in acts:
        sport = a.get("activityType", {}).get("typeKey", "")
        if "running" not in sport:
            continue
        dist = (a.get("distance", 0) or 0) / 1000
        if dist >= 21.0:
            d = a.get("startTimeLocal", "")[:10]
            dur = (a.get("duration", 0) or 0) / 60
            moving = (a.get("movingDuration", 0) or 0) / 60
            avg_hr = a.get("averageHR", 0) or 0
            max_hr = a.get("maxHR", 0) or 0
            kcal = a.get("calories", 0) or 0
            pace = a.get("averageSpeed", 0) or 0
            if pace > 0:
                ps = (1 / pace) * 1000
                pm = int(ps // 60)
                ps2 = int(ps % 60)
                pace_str = f"{pm}:{ps2:02d}"
            else:
                pace_str = "--"
            all_runs.append({
                "date": d,
                "dist": dist,
                "elapsed": dur,
                "moving": moving,
                "avg_hr": avg_hr,
                "max_hr": max_hr,
                "kcal": kcal,
                "pace": pace_str,
                "name": a.get("activityName", "")
            })
    if len(acts) < 100:
        break
    page += 1
    if page > 10:
        break

all_runs.sort(key=lambda x: x["date"])
print(f"=== ALL RUNS 21km+ (Total: {len(all_runs)}) ===")
for i, r in enumerate(all_runs, 1):
    em = int(r["elapsed"])
    es = int((r["elapsed"] - em) * 60)
    mm2 = int(r["moving"])
    ms2 = int((r["moving"] - mm2) * 60)
    print(f"{i}. {r['date']} | {r['dist']:.2f}km | Elapsed: {em}m{es:02d}s | Moving: {mm2}m{ms2:02d}s | Pace: {r['pace']}/km | AvgHR: {r['avg_hr']:.0f} | MaxHR: {r['max_hr']:.0f} | Kcal: {r['kcal']:.0f}")
    print(f"   {r['name']}")

# PR: fastest elapsed for HM distance (21-22.5km)
hm_runs = [r for r in all_runs if 21.0 <= r["dist"] <= 22.5]
if hm_runs:
    pr = min(hm_runs, key=lambda x: x["elapsed"])
    print(f"\n=== HM DISTANCE PR (Fastest Elapsed, 21-22.5km) ===")
    em = int(pr["elapsed"])
    es = int((pr["elapsed"] - em) * 60)
    print(f"Date: {pr['date']} | Dist: {pr['dist']:.2f}km | Elapsed: {em}m{es:02d}s | Pace: {pr['pace']}/km | AvgHR: {pr['avg_hr']:.0f}")

    # Moving time PR
    pr_moving = min(hm_runs, key=lambda x: x["moving"])
    mm2 = int(pr_moving["moving"])
    ms2 = int((pr_moving["moving"] - mm2) * 60)
    print(f"\n=== HM DISTANCE PR (Fastest Moving Time) ===")
    print(f"Date: {pr_moving['date']} | Dist: {pr_moving['dist']:.2f}km | Moving: {mm2}m{ms2:02d}s | Pace: {pr_moving['pace']}/km | AvgHR: {pr_moving['avg_hr']:.0f}")
