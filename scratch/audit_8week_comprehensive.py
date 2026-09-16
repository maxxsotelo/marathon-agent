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

start_date = date(2026, 6, 22)
end_date = date(2026, 8, 15)

acts = client.get_activities_by_date(start_date.isoformat(), end_date.isoformat())

print(f"Total activities from {start_date} to {end_date}: {len(acts)}")

# Break down running activities
running_acts = [a for a in acts if "running" in a.get("activityType", {}).get("typeKey", "")]
print(f"Total running sessions: {len(running_acts)}")

total_run_dist = sum((a.get("distance") or 0) for a in running_acts) / 1000
total_run_time_s = sum((a.get("duration") or 0) for a in running_acts)
total_run_elev = sum((a.get("elevationGain") or 0) for a in running_acts)

print(f"Total running distance: {total_run_dist:.2f} km")
print(f"Total running time: {total_run_time_s/3600:.1f} hours ({total_run_time_s//60} mins)")
print(f"Total elevation gained: +{total_run_elev:.0f} m")

# Group by week
weeks = {}
curr = start_date
while curr <= end_date:
    mon = curr - timedelta(days=curr.weekday())
    sun = mon + timedelta(days=6)
    k = f"{mon.strftime('%b %d')} - {sun.strftime('%b %d')}"
    if k not in weeks:
        weeks[k] = {
            "start": mon,
            "end": sun,
            "runs": [],
            "bikes": [],
            "swims": [],
            "strength": [],
            "hiit": []
        }
    curr += timedelta(days=7)

for a in acts:
    d_str = a.get("startTimeLocal", "")[:10]
    d = date.fromisoformat(d_str)
    t = a.get("activityType", {}).get("typeKey", "?")
    name = a.get("activityName", "")
    for k, w in weeks.items():
        if w["start"] <= d <= w["end"]:
            if "running" in t:
                w["runs"].append(a)
            elif "cycling" in t:
                w["bikes"].append(a)
            elif "swimming" in t:
                w["swims"].append(a)
            elif "strength" in t:
                w["strength"].append(a)
            else:
                w["hiit"].append(a)

print("\n--- WEEK BY WEEK AUDIT ---")
for k, w in sorted(weeks.items(), key=lambda x: x[1]["start"]):
    r_km = sum((a.get("distance") or 0)/1000 for a in w["runs"])
    r_time = sum((a.get("duration") or 0)/60 for a in w["runs"])
    lr = max([(a.get("distance") or 0)/1000 for a in w["runs"]], default=0)
    p_str = "-"
    if r_km > 0:
        p_sec = (r_time * 60) / r_km
        p_str = f"{int(p_sec//60)}:{int(p_sec%60):02d}/km"
    b_km = sum((a.get("distance") or 0)/1000 for a in w["bikes"])
    s_m = sum((a.get("distance") or 0) for a in w["swims"])
    st_c = len([a for a in w["strength"] if (a.get("duration") or 0) >= 600])
    h_c = len(w["hiit"])
    print(f"{k:17s} | Run: {r_km:5.1f}km ({len(w['runs']):2d} runs, LR: {lr:4.1f}km, Pace: {p_str}) | Bike: {b_km:4.1f}km | Swim: {s_m:4.0f}m | Strength: {st_c} | Cross/HIIT: {h_c}")

# Let's inspect pace vs HR progression over time for easy/long runs:
print("\n--- LONG RUN EVOLUTION ---")
for r in sorted(running_acts, key=lambda x: x.get("startTimeLocal", "")):
    dist = (r.get("distance") or 0) / 1000
    if dist >= 14.0:
        dur = (r.get("duration") or 0) / 60
        ahr = r.get("averageHR")
        ae = r.get("aerobicTrainingEffect")
        speed = r.get("averageSpeed")
        p = f"{int(1000/speed//60)}:{int(1000/speed%60):02d}/km" if speed else "-"
        d = r.get("startTimeLocal", "")[:10]
        print(f"  {d} | {dist:5.2f} km | {dur:4.0f} min ({p}) | Avg HR: {ahr} bpm | TE: {ae} | {r.get('activityName')}")
