"""
full_kiat_engine_run.py
Runs the full Kiat Engine compute on actual Garmin data.
"""
import os, sys
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from core_physiological_engine import PhysiologicalEngine, SleepData, HRVData, ActivityWindow

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 28)
today_iso = today.isoformat()

# Fetch Sleep
sleep_score = None
total_sleep = 0
try:
    sleep = client.get_sleep_data(today_iso)
    if sleep:
        sleep_score = sleep.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value')
        total_sleep = sleep.get('dailySleepDTO', {}).get('sleepTimeSeconds', 0)
except Exception as e:
    print(f"Sleep error: {e}")

sleep_data = SleepData(
    sleep_score=float(sleep_score) if sleep_score else None,
    total_sleep_secs=float(total_sleep)
)

# Fetch HRV
last_night = None
weekly = None
try:
    hrv = client.get_hrv_data(today_iso)
    if hrv:
        last_night = hrv.get('hrvSummary', {}).get('lastNightAvg')
        weekly = hrv.get('hrvSummary', {}).get('weeklyAvg')
except Exception as e:
    print(f"HRV error: {e}")

hrv_data = HRVData(
    last_night_avg_ms=float(last_night) if last_night else None,
    weekly_avg_ms=float(weekly) if weekly else None
)

# Fetch Readiness / Recovery
recovery_hrs = 0
try:
    readiness = client.get_training_readiness(today_iso)
    if readiness:
        recovery_hrs = float(readiness.get('recoveryTime', 0))
except Exception: pass

# Fetch Stress
stress = 25.0
try:
    summary = client.get_user_summary(today_iso)
    s = summary.get('averageStressLevel')
    if s is not None:
        stress = float(s)
except Exception: pass

# Fetch Activity Window (last 28 days for ACWR)
start_28 = today - timedelta(days=28)
activities = []
try:
    acts = client.get_activities_by_date(start_28.isoformat(), today_iso)
    for act in acts:
        # Convert date string
        dt_str = act.get('startTimeLocal', '')
        if not dt_str: continue
        try:
            dt_naive = datetime.fromisoformat(dt_str)
            act_date = dt_naive.replace(tzinfo=timezone.utc) - timedelta(hours=8)
        except:
            continue
            
        dist_km = (act.get('distance') or 0) / 1000.0
        load = act.get('activityTrainingLoad') or 0.0
        t = act.get('activityType', {}).get('typeKey', 'other')
        
        activities.append({
            'date': act_date,
            'distance_km': dist_km,
            'activity_load': float(load),
            'activity_type': t
        })
except Exception as e:
    print(f"Activity window error: {e}")

act_window = ActivityWindow(runs=activities)

now_utc = datetime.now(timezone.utc)

engine = PhysiologicalEngine()
report = engine.compute(
    sleep=sleep_data,
    hrv=hrv_data,
    recovery_hours=recovery_hrs,
    activity_end_time_utc=now_utc - timedelta(hours=12),
    rolling_stress_3d=stress,
    activity_window=act_window,
    laps=[] # We are just doing morning diagnostics, no lap analysis right now
)

print(report.summary_text)
print("\n--- KIAT ENGINE MORNING DUMP ---")
print(f"Raw TRS:          {report.trs_score:.1f}")
print(f"Status:           {report.training_status}")
print(f"ACWR:             {report.acwr:.2f}")
print(f"Speed Veto:       {report.speed_veto}")
