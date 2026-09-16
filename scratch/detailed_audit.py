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

today = date.today()

# Get 8 weeks of data
start_8w = today - timedelta(days=56)
acts_8w = client.get_activities_by_date(start_8w.isoformat(), today.isoformat())

print(f"Total activities in 8w: {len(acts_8w)}")

# Let's break down weekly totals from Mon to Sun for all 8 weeks
weeks = {}
for i in range(8):
    # compute monday and sunday of each week
    # current week is i=0
    curr_mon = today - timedelta(days=today.weekday()) - timedelta(weeks=7-i)
    curr_sun = curr_mon + timedelta(days=6)
    wk_label = f"{curr_mon.strftime('%b %d')} - {curr_sun.strftime('%b %d')}"
    weeks[wk_label] = {
        "start": curr_mon,
        "end": curr_sun,
        "run_km": 0.0,
        "run_time_s": 0.0,
        "longest_run": 0.0,
        "run_count": 0,
        "bike_km": 0.0,
        "swim_m": 0.0,
        "strength_count": 0,
        "hiit_count": 0,
        "acts": []
    }

for a in acts_8w:
    d_str = a.get("startTimeLocal", "")[:10]
    d = date.fromisoformat(d_str)
    t = a.get("activityType", {}).get("typeKey", "?")
    name = a.get("activityName", "?")
    dist = (a.get("distance") or 0) / 1000
    dur = a.get("duration") or 0
    dur_m = dur / 60
    
    for label, wk in weeks.items():
        if wk["start"] <= d <= wk["end"]:
            wk["acts"].append(a)
            if "running" in t:
                wk["run_km"] += dist
                wk["run_time_s"] += dur
                wk["run_count"] += 1
                if dist > wk["longest_run"]:
                    wk["longest_run"] = dist
            elif "cycling" in t:
                wk["bike_km"] += dist
            elif "swimming" in t:
                wk["swim_m"] += (a.get("distance") or 0)
            elif "strength" in t:
                if dur >= 600: # at least 10 min
                    wk["strength_count"] += 1
            elif "hiit" in t or "cardio" in t or "boxing" in name.lower() or "muay" in name.lower() or "basketball" in name.lower():
                wk["hiit_count"] += 1

print("\n=== 8-WEEK PROGRESSION TABLE ===")
for label, wk in weeks.items():
    pace_str = "-"
    if wk["run_km"] > 0:
        p_sec = wk["run_time_s"] / wk["run_km"]
        pace_str = f"{int(p_sec//60)}:{int(p_sec%60):02d}/km"
    print(f"{label:17s} | Run: {wk['run_km']:5.1f} km ({wk['run_count']} runs, LR: {wk['longest_run']:4.1f} km, Pace: {pace_str}) | Bike: {wk['bike_km']:4.1f} km | Swim: {wk['swim_m']:4.0f} m | Strength: {wk['strength_count']} | Cross/HIIT: {wk['hiit_count']}")

# Recent 7-14 days detail
print("\n=== LAST 14 DAYS CHRONOLOGICAL LOG (Aug 01 to Aug 14) ===")
acts_14d = client.get_activities_by_date((today - timedelta(days=14)).isoformat(), today.isoformat())
# sort chronological
acts_14d = sorted(acts_14d, key=lambda x: x.get("startTimeLocal", ""))

for a in acts_14d:
    t = a.get("activityType", {}).get("typeKey", "?")
    name = a.get("activityName", "?")
    d = a.get("startTimeLocal", "?")[:16]
    dist = (a.get("distance") or 0) / 1000
    dur = (a.get("duration") or 0) / 60
    ahr = a.get("averageHR", "-")
    mhr = a.get("maxHR", "-")
    ae = a.get("aerobicTrainingEffect", "-")
    an = a.get("anaerobicTrainingEffect", "-")
    cal = a.get("calories", "-")
    label = a.get("trainingEffectLabel", "-")
    print(f"[{d}] {t:18s} | {dist:5.2f} km | {dur:3.0f} min | HR: {str(ahr):>3}/{str(mhr):<3} bpm | TE: Ae{str(ae)[:3]}/An{str(an)[:3]} | {name} ({label})")
