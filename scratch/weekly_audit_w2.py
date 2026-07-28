import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Week 2: June 29 - July 5
week_start = "2026-06-29"
week_end = "2026-07-05"

acts = client.get_activities_by_date(week_start, week_end)

print("=" * 70)
print("  WEEK 2 ACTIVITY AUDIT — Jun 29 to Jul 5, 2026")
print("=" * 70)

total_run_km = 0
total_run_time = 0
total_gym_time = 0
run_days = []

for a in sorted(acts, key=lambda x: x.get("startTimeLocal", "")):
    sport = a.get("activityType", {}).get("typeKey", "")
    name = a.get("activityName", "")
    dist = (a.get("distance", 0) or 0) / 1000
    dur_sec = a.get("duration", 0) or 0
    dur_min = dur_sec / 60
    avg_hr = a.get("averageHR", 0) or 0
    aer_te = a.get("aerobicTrainingEffect", 0) or 0
    start = a.get("startTimeLocal", "")[:10]
    day = a.get("startTimeLocal", "")[:10]

    if "running" in sport:
        pace_secs = dur_sec / dist if dist > 0 else 0
        pace_str = f"{int(pace_secs//60)}:{int(pace_secs%60):02d}/km"
        total_run_km += dist
        total_run_time += dur_min
        run_days.append(day)
        print(f"\n[RUN] {start} | {name[:40]}")
        print(f"  Distance: {dist:.2f} km | Pace: {pace_str} | Duration: {dur_min:.0f} min")
        print(f"  Avg HR: {avg_hr:.0f} bpm | Aer TE: {aer_te:.1f}")
    elif "strength" in sport:
        total_gym_time += dur_min
        print(f"\n[GYM] {start} | {name[:40]}")
        print(f"  Duration: {dur_min:.0f} min | Avg HR: {avg_hr:.0f} bpm | Aer TE: {aer_te:.1f}")

print()
print("=" * 70)
print("  WEEK 2 SUMMARY")
print("=" * 70)
print(f"  Total Running Distance : {total_run_km:.2f} km")
print(f"  Total Running Time     : {total_run_time:.0f} min ({total_run_time/60:.1f} hrs)")
print(f"  Total Run Sessions     : {len(run_days)}")
print(f"  Total Gym Time         : {total_gym_time:.0f} min")

# ACWR
# 7-day acute (Jun 29-Jul 5)
# 28-day chronic: pull last 28 days of running
all_acts = client.get_activities_by_date("2026-06-07", week_end)
weekly_km = {}
for a in all_acts:
    sport = a.get("activityType", {}).get("typeKey", "")
    if "running" not in sport:
        continue
    day = a.get("startTimeLocal", "")[:10]
    if not day:
        continue
    d = date.fromisoformat(day)
    # Get ISO week start (Monday)
    week_s = d - timedelta(days=d.weekday())
    key = week_s.isoformat()
    dist_km = (a.get("distance", 0) or 0) / 1000
    weekly_km[key] = weekly_km.get(key, 0) + dist_km

print()
print("  ACWR COMPUTATION:")
acute = total_run_km
# chronic = avg of last 4 full weeks (ending Jun 28)
chronic_weeks = []
ref = date(2026, 6, 28)
for i in range(4):
    w_end = ref - timedelta(days=7*i)
    w_start = w_end - timedelta(days=6)
    w_acts = [a for a in all_acts if "running" in a.get("activityType",{}).get("typeKey","")
              and w_start.isoformat() <= (a.get("startTimeLocal","")[:10] or "0") <= w_end.isoformat()]
    w_km = sum((a.get("distance",0) or 0)/1000 for a in w_acts)
    chronic_weeks.append(w_km)
    print(f"    Chronic week -{i+1} ({w_start} to {w_end}): {w_km:.2f} km")

chronic_avg = sum(chronic_weeks) / len(chronic_weeks) if chronic_weeks else 1
acwr = acute / chronic_avg if chronic_avg > 0 else 0
print(f"  Acute (Week 2 total): {acute:.2f} km")
print(f"  Chronic avg (4wk):    {chronic_avg:.2f} km/week")
print(f"  ACWR:                 {acwr:.3f}")
if acwr < 0.8:
    print("  STATUS: [UNDERTRAINING] — Below optimal zone")
elif acwr <= 1.3:
    print("  STATUS: [SWEET SPOT] — Optimal training load")
elif acwr <= 1.5:
    print("  STATUS: [WARNING] — Elevated injury risk")
else:
    print("  STATUS: [DANGER] — Structural deload mandatory")
