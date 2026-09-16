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
start = today - timedelta(days=28)

print(f"=== COMPREHENSIVE 4-WEEK AUDIT ({start} to {today}) ===")

# 1. Activities
acts = client.get_activities_by_date(start.isoformat(), today.isoformat())
print(f"\nTotal activities in 28 days: {len(acts)}")

# Group activities by week (Monday to Sunday)
weeks = {}
for a in acts:
    dt_str = a.get("startTimeLocal", "")[:10]
    dt = date.fromisoformat(dt_str)
    # Mon of that week
    mon = dt - timedelta(days=dt.weekday())
    sun = mon + timedelta(days=6)
    wk_key = f"{mon.isoformat()} to {sun.isoformat()}"
    if wk_key not in weeks:
        weeks[wk_key] = []
    weeks[wk_key].append(a)

for wk_key in sorted(weeks.keys()):
    w_acts = weeks[wk_key]
    print(f"\n==========================================")
    print(f"WEEK: {wk_key}")
    print(f"==========================================")
    run_km = 0.0
    run_time = 0.0
    bike_km = 0.0
    swim_m = 0.0
    strength_count = 0
    hiit_count = 0
    
    for a in sorted(w_acts, key=lambda x: x.get("startTimeLocal", "")):
        t = a.get("activityType", {}).get("typeKey", "?")
        name = a.get("activityName", "?")
        d = a.get("startTimeLocal", "?")[:16]
        dist = (a.get("distance") or 0) / 1000
        dur = (a.get("duration") or 0) / 60
        ahr = a.get("averageHR", "-")
        mhr = a.get("maxHR", "-")
        ae = a.get("aerobicTrainingEffect", "-")
        an = a.get("anaerobicTrainingEffect", "-")
        label = a.get("trainingEffectLabel", "-")
        
        if "running" in t:
            run_km += dist
            run_time += dur
        elif "cycling" in t:
            bike_km += dist
        elif "swimming" in t:
            swim_m += (a.get("distance") or 0)
        elif "strength" in t:
            strength_count += 1
        elif "hiit" in t or "cardio" in t or "boxing" in name.lower() or "muay" in name.lower():
            hiit_count += 1
            
        print(f"  {d} | {t:18s} | {dist:5.2f}km | {dur:4.0f}m | HR: {str(ahr):>3}/{str(mhr):<3} | TE: Ae{str(ae)[:3]}/An{str(an)[:3]} | {name} ({label})")
    
    print(f"  --> TOTALS: Run: {run_km:.2f} km ({run_time:.0f} mins) | Bike: {bike_km:.2f} km | Swim: {swim_m:.0f} m | Strength: {strength_count} | Cardio/HIIT: {hiit_count}")

# 2. Vitals & Recovery metrics
print("\n==========================================")
print("TODAY'S VITALS & RECOVERY STATUS")
print("==========================================")
try:
    stats = client.get_user_summary(today.isoformat())
    print(f"  Resting Heart Rate: {stats.get('restingHeartRate')} bpm")
    print(f"  Body Battery:       {stats.get('bodyBatteryMostRecentValue')} (High: {stats.get('bodyBatteryHighestValue')}, Low: {stats.get('bodyBatteryLowestValue')})")
    print(f"  Stress Level Avg:   {stats.get('averageStressLevel')}")
except Exception as e:
    print(f"  Summary error: {e}")

try:
    sleep = client.get_sleep_data(today.isoformat())
    if sleep and "dailySleepDTO" in sleep:
        dto = sleep["dailySleepDTO"]
        sec = dto.get("sleepTimeSeconds", 0)
        print(f"  Sleep Duration:     {sec/3600:.1f} hrs ({sec//60} mins)")
        print(f"  Sleep Score:        {dto.get('sleepScores', {}).get('overall', {}).get('value')}")
        print(f"  Deep/Light/REM/Awake: {dto.get('deepSleepSeconds',0)/60:.0f}m / {dto.get('lightSleepSeconds',0)/60:.0f}m / {dto.get('remSleepSeconds',0)/60:.0f}m / {dto.get('awakeSleepSeconds',0)/60:.0f}m")
except Exception as e:
    print(f"  Sleep error: {e}")

try:
    hrv = client.get_hrv_data(today.isoformat())
    if hrv and "hrvSummary" in hrv:
        s = hrv["hrvSummary"]
        print(f"  HRV Status:         {s.get('status')}")
        print(f"  HRV Weekly Avg:     {s.get('weeklyAvg')} ms")
        print(f"  HRV Last Night:     {s.get('lastNightAvg')} ms (5m peak: {s.get('lastNight5MinHigh')} ms)")
        print(f"  HRV Baseline:       {s.get('baselineBalancedLow')} - {s.get('baselineBalancedUpper')} ms")
except Exception as e:
    print(f"  HRV error: {e}")

try:
    readiness = client.get_training_readiness(today.isoformat())
    print(f"  Training Readiness: {readiness}")
except Exception as e:
    print(f"  Readiness error: {e}")

try:
    recovery = client.get_recovery_time(today.isoformat())
    print(f"  Recovery Time:      {recovery} hours")
except Exception as e:
    # try user summary
    pass
