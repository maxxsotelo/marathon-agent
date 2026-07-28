import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

print("=" * 70)
print("  8-WEEK RUNNING HISTORY + ACWR PROJECTION")
print("=" * 70)

# Pull last 8 weeks of running
all_acts = client.get_activities_by_date("2026-05-11", "2026-07-06")
running = [a for a in all_acts if "running" in a.get("activityType", {}).get("typeKey", "")]

# Build per-week buckets (Monday-based)
weeks = {}
for a in running:
    day_str = (a.get("startTimeLocal") or "")[:10]
    if not day_str:
        continue
    d = date.fromisoformat(day_str)
    monday = d - timedelta(days=d.weekday())
    key = monday.isoformat()
    dist = (a.get("distance") or 0) / 1000
    weeks.setdefault(key, {"km": 0, "runs": 0, "longest": 0, "sessions": []})
    weeks[key]["km"] += dist
    weeks[key]["runs"] += 1
    weeks[key]["longest"] = max(weeks[key]["longest"], dist)
    weeks[key]["sessions"].append({
        "date": day_str,
        "dist": dist,
        "pace": (a.get("duration") or 0) / (dist * 60) if dist else 0,
        "hr": a.get("averageHR") or 0,
        "aer_te": a.get("aerobicTrainingEffect") or 0,
        "name": (a.get("activityName") or "")[:35],
    })

sorted_weeks = sorted(weeks.keys())
print(f"\n{'Week (Mon)':<14} {'Total km':<10} {'Runs':<6} {'Longest':<10} {'Avg Pace':<10} {'Note'}")
print("-" * 75)

weekly_km_list = []
for wk in sorted_weeks:
    d = weeks[wk]
    km = d["km"]
    runs = d["runs"]
    longest = d["longest"]
    weekly_km_list.append(km)
    # avg pace across sessions
    total_dur = sum(s["pace"] * s["dist"] * 60 for s in d["sessions"] if s["dist"] > 0)
    total_dist = sum(s["dist"] for s in d["sessions"])
    avg_pace_sec = total_dur / total_dist if total_dist > 0 else 0
    avg_pace_str = f"{int(avg_pace_sec//60)}:{int(avg_pace_sec%60):02d}/km" if avg_pace_sec > 0 else "N/A"

    note = ""
    if wk == "2026-06-29":
        note = "<-- Week 2 (COMPLETED)"
    elif wk == "2026-07-06":
        note = "<-- Week 3 (CURRENT)"

    print(f"{wk:<14} {km:<10.2f} {runs:<6} {longest:<10.2f} {avg_pace_str:<10} {note}")

# Now compute ACWR for today and projections
today = date.today()
# 7-day acute window: Jun 30 - Jul 6 (today is Jul 6, no run yet)
acute_acts = [a for a in running if "2026-06-30" <= (a.get("startTimeLocal") or "")[:10] <= "2026-07-06"]
acute_km = sum((a.get("distance") or 0) / 1000 for a in acute_acts)

# 28-day chronic: rolling 4 weeks
chronic_weeks = []
for i in range(4):
    w_end_d = today - timedelta(days=7*i + 1)
    w_start_d = w_end_d - timedelta(days=6)
    w_acts = [a for a in running if w_start_d.isoformat() <= (a.get("startTimeLocal") or "")[:10] <= w_end_d.isoformat()]
    w_km = sum((a.get("distance") or 0) / 1000 for a in w_acts)
    chronic_weeks.append(w_km)

chronic_avg = sum(chronic_weeks) / len(chronic_weeks)
acwr_now = acute_km / chronic_avg if chronic_avg > 0 else 0

print()
print("=" * 70)
print("  CURRENT ACWR STATUS (as of Jul 6 morning, before today's session)")
print("=" * 70)
print(f"  7-day Acute (Jun 30 - Jul 6): {acute_km:.2f} km")
for i, w in enumerate(chronic_weeks):
    w_end_d = today - timedelta(days=7*i + 1)
    w_start_d = w_end_d - timedelta(days=6)
    print(f"  Chronic week {i+1} ({w_start_d} to {w_end_d}): {w:.2f} km")
print(f"  Chronic Avg (28d): {chronic_avg:.2f} km/week")
print(f"  Current ACWR: {acwr_now:.3f}")

# Week 3 projections
print()
print("=" * 70)
print("  WEEK 3 PROJECTIONS — OPTION A vs OPTION B")
print("=" * 70)

# Week 3 proposed plan (Monday-Sunday)
# Option A: No run today, run Tue/Wed/Thu/Fri/Sat
# Option B: Run today evening + Tue/Wed/Thu/Fri/Sat

w3_plan = {
    "Mon Jul 6":  {"gym": "Pull", "run_A": 0,     "run_B": 9},
    "Tue Jul 7":  {"gym": None,   "run_A": 10,    "run_B": 10},
    "Wed Jul 8":  {"gym": None,   "run_A": 10,    "run_B": 10},
    "Thu Jul 9":  {"gym": "Legs+Core", "run_A": 0, "run_B": 0},
    "Fri Jul 10": {"gym": None,   "run_A": 10,    "run_B": 10},
    "Sat Jul 11": {"gym": "Push", "run_A": 0,     "run_B": 0},
    "Sun Jul 12": {"gym": None,   "run_A": 17,    "run_B": 17},
}

total_A = sum(v["run_A"] for v in w3_plan.values())
total_B = sum(v["run_B"] for v in w3_plan.values())

print(f"\n{'Day':<14} {'Gym':<14} {'Run A':<10} {'Run B':<10}")
print("-" * 50)
for day, v in w3_plan.items():
    gym = v["gym"] or "-"
    run_a = f"{v['run_A']} km" if v["run_A"] > 0 else "Rest"
    run_b = f"{v['run_B']} km" if v["run_B"] > 0 else "Rest"
    print(f"{day:<14} {gym:<14} {run_a:<10} {run_b:<10}")

print(f"\n  Option A Total: {total_A:.0f} km/week")
print(f"  Option B Total: {total_B:.0f} km/week")

# ACWR projections end of week
print()
# Option A adds 47 km to week (current acute 44.53)
# At end of week the 7-day window is Jul 6-12
# Approximate: new acute ~= runs from Jul 6-12

# Current sessions in 7-day window (Jun 30 - today): 44.53 km
# For end of week Jul 12 window is Jul 6-12
# Jun 30-Jul 5 runs drop off (those were: Jul 3=10.22, Jul 4=15.17, Jul 5=9.08 = 34.47km drop)
# New runs Jul 6-12 add in

print(f"  Projected ACWR end of Week 3 (Jul 12):")
# Runs that drop off from current 7d window when window moves to Jul 6-12:
# Jul 1: 10.06, Jul 3: 10.22, Jul 4: 15.17, Jul 5: 9.08 = 44.53 total
# All these drop off. New acute = only Week 3 runs

acwr_A_end = total_A / chronic_avg if chronic_avg > 0 else 0
acwr_B_end = total_B / chronic_avg if chronic_avg > 0 else 0
print(f"  Option A: {total_A} km | ACWR = {acwr_A_end:.3f}")
print(f"  Option B: {total_B} km | ACWR = {acwr_B_end:.3f}")
