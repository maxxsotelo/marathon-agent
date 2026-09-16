import os
from datetime import date
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
print(f"=== GARMIN PRE-SLEEP AUDIT: {today} ===")

# 1. Activities today
acts = client.get_activities_by_date(today.isoformat(), today.isoformat())
print(f"\nActivities today: {len(acts)}")
for a in acts:
    act_id = a.get("activityId")
    name = a.get("activityName")
    t = a.get("activityType", {}).get("typeKey")
    dist = (a.get("distance") or 0) / 1000
    dur = (a.get("duration") or 0) / 60
    mov_dur = (a.get("movingDuration") or 0) / 60
    ahr = a.get("averageHR")
    mhr = a.get("maxHR")
    ae = a.get("aerobicTrainingEffect")
    an = a.get("anaerobicTrainingEffect")
    elev = a.get("elevationGain")
    cal = a.get("calories")
    speed = a.get("averageSpeed")
    p_str = "-"
    if speed and speed > 0:
        s = 1000 / speed
        p_str = f"{int(s//60)}:{int(s%60):02d}/km"
    
    print(f"\n[ACTIVITY] ID: {act_id} | {t} | {name}")
    print(f"  Distance:     {dist:.2f} km | Moving Time: {mov_dur:.1f} min | Pace: {p_str}")
    print(f"  Heart Rate:   {ahr} avg / {mhr} max bpm")
    print(f"  Training Eff: Aerobic {ae} | Anaerobic {an}")
    print(f"  Elev / Cal:   +{elev} m | {cal} kcal")

    # Lap details if run
    if "running" in t or "cycling" in t:
        splits = client.get_activity_splits(act_id)
        if splits and "lapDTOs" in splits:
            print("  --- Laps ---")
            for idx, lap in enumerate(splits["lapDTOs"]):
                ldist = (lap.get("distance") or 0) / 1000
                lmov = (lap.get("movingDuration") or 0) / 60
                lhr = lap.get("averageHR")
                lmhr = lap.get("maxHR")
                lspeed = lap.get("averageSpeed")
                lp_str = "-"
                if lspeed and lspeed > 0:
                    ls = 1000 / lspeed
                    lp_str = f"{int(ls//60)}:{int(ls%60):02d}/km"
                print(f"    Lap {idx+1:2d}: {ldist:4.2f} km | {lmov:4.2f}m ({lp_str}) | HR: {str(lhr):>3}/{str(lmhr):<3} bpm")

# 2. Daily User Summary & Vitals
summary = client.get_user_summary(today.isoformat())
print("\n--- DAILY USER SUMMARY ---")
print(f"  Steps:             {summary.get('totalSteps')} / Goal: {summary.get('dailyStepGoal')}")
print(f"  Distance:          {(summary.get('totalDistanceMeters') or 0)/1000:.2f} km")
print(f"  Active Calories:   {summary.get('activeKilocalories')} kcal | Total: {summary.get('totalKilocalories')} kcal")
print(f"  Resting HR:        {summary.get('restingHeartRate')} bpm (Min: {summary.get('minHeartRate')}, Max: {summary.get('maxHeartRate')})")
print(f"  Body Battery:      Current: {summary.get('bodyBatteryMostRecentValue')} | High: {summary.get('bodyBatteryHighestValue')} | Low: {summary.get('bodyBatteryLowestValue')}")
print(f"  Average Stress:    {summary.get('averageStressLevel')} / 100")
print(f"  Stress Duration:   Rest: {summary.get('restStressDuration')}s | Low: {summary.get('lowStressDuration')}s | Med: {summary.get('mediumStressDuration')}s | High: {summary.get('highStressDuration')}s")

# 3. Training Readiness & Recovery
print("\n--- RECOVERY & READINESS ---")
try:
    readiness = client.get_training_readiness(today.isoformat())
    print(f"  Training Readiness: {readiness}")
except Exception as e:
    print(f"  Readiness: {e}")

try:
    hrv = client.get_hrv_data(today.isoformat())
    if hrv and "hrvSummary" in hrv:
        s = hrv["hrvSummary"]
        print(f"  HRV Status:        {s.get('status')}")
        print(f"  HRV Weekly Avg:    {s.get('weeklyAvg')} ms")
        print(f"  HRV Last Night:    {s.get('lastNightAvg')} ms (5m peak: {s.get('lastNight5MinHigh')} ms)")
except Exception as e:
    print(f"  HRV: {e}")
