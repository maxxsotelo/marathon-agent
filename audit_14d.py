"""Temporary script: Pull last 14 days of Garmin activities for analysis."""
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
start = today - timedelta(days=14)

acts = client.get_activities_by_date(start.isoformat(), today.isoformat())

def pace_str(speed, act_type):
    if not speed or speed <= 0:
        return "-"
    if act_type == "running":
        s = 1000 / speed
        return f"{int(s // 60)}:{int(s % 60):02d}/km"
    elif act_type == "cycling":
        return f"{speed * 3.6:.1f} km/h"
    return "-"

print(f"=== 14-DAY ACTIVITY LOG: {start} to {today} ({len(acts)} activities) ===\n")

for a in acts:
    t = a.get("activityType", {}).get("typeKey", "?")
    name = a.get("activityName", "?")
    d = a.get("startTimeLocal", "?")[:16]
    dist = (a.get("distance") or 0) / 1000
    dur = (a.get("duration") or 0) / 60
    ahr = a.get("averageHR", "-")
    mhr = a.get("maxHR", "-")
    ae = a.get("aerobicTrainingEffect", "-")
    an = a.get("anaerobicTrainingEffect", "-")
    elev = a.get("elevationGain") or 0
    cal = a.get("calories", "-")
    label = a.get("trainingEffectLabel", "-")
    p = pace_str(a.get("averageSpeed"), t)

    print(f"  {d} | {t:20s} | {name}")
    print(f"    Dist: {dist:.2f}km | Dur: {dur:.0f}min | Pace: {p}")
    print(f"    HR: {ahr}/{mhr} | TE: Ae{ae}/An{an} | Elev: +{elev:.0f}m | Cal: {cal} | Benefit: {label}")
    print()

# HRV
print("=== HRV SUMMARY ===")
hrv = client.get_hrv_data(today.isoformat())
if hrv and "hrvSummary" in hrv:
    s = hrv["hrvSummary"]
    print(f"  Weekly Avg:     {s.get('weeklyAvg')} ms")
    print(f"  Last Night Avg: {s.get('lastNightAvg')} ms")
    print(f"  Last Night 5m:  {s.get('lastNight5MinHigh')} ms")
    print(f"  Baseline Low:   {s.get('baselineLowUpper')} ms")
    print(f"  Baseline Bal:   {s.get('baselineBalancedLow')} ms")
    print(f"  Status:         {s.get('status')}")

# Training status
print("\n=== TRAINING STATUS ===")
try:
    ts = client.get_training_status(today.isoformat())
    print(f"  VO2 Max:          {ts.get('mostRecentVO2Max')}")
    print(f"  Training Status:  {ts.get('mostRecentTrainingStatus')}")
    print(f"  Load Balance:     {ts.get('mostRecentTrainingLoadBalance')}")
except Exception as e:
    print(f"  (Could not fetch: {e})")
