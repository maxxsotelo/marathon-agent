"""
fetch_friday_vitals_audit.py
"""
import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 8, 14)
print("=== VITALS FOR", today.isoformat(), "===")

# Sleep
try:
    sleep_data = client.get_sleep_data(today.isoformat())
    dto = sleep_data.get("dailySleepDTO", {})
    sleep_hrs = (dto.get("sleepTimeSeconds") or 0) / 3600
    sleep_score = dto.get("sleepScores", {}).get("overall", {}).get("value")
    print(f"Sleep Duration: {sleep_hrs:.2f} hrs | Sleep Score: {sleep_score}")
except Exception as e:
    print("Sleep error:", e)

# HRV
try:
    hrv = client.get_hrv_data(today.isoformat())
    hrv_summary = hrv.get("hrvSummary", {})
    print(f"Last Night HRV Avg: {hrv_summary.get('lastNightAvg')} ms | 7d Avg: {hrv_summary.get('weeklyAvg')} ms | Status: {hrv_summary.get('status')}")
    print(f"HRV Baseline: {hrv_summary.get('baseline', {})}")
except Exception as e:
    print("HRV error:", e)

# RHR & Body Battery
try:
    stats = client.get_user_summary(today.isoformat())
    print(f"Resting HR: {stats.get('restingHeartRate')} bpm")
    print(f"Body Battery: Most Recent: {stats.get('bodyBatteryMostRecentValue')}, High: {stats.get('bodyBatteryHighestValue')}, Low: {stats.get('bodyBatteryLowestValue')}")
except Exception as e:
    print("Stats error:", e)

# Training Readiness / Status if available
try:
    readiness = client.get_training_readiness(today.isoformat())
    print("Training Readiness:", json.dumps(readiness, indent=2))
except Exception as e:
    print("Training Readiness error/not available:", e)

# Last 14 days activities
start_14d = today - timedelta(days=14)
acts = client.get_activities_by_date(start_14d.isoformat(), today.isoformat())
print("\n=== LAST 14 DAYS ACTIVITIES ===")
for a in acts:
    st = a.get("startTimeLocal", "")[:10]
    tkey = a.get("activityType", {}).get("typeKey")
    dist = a.get("distance", 0) / 1000.0
    dur = a.get("duration", 0) / 60.0
    te = a.get("aerobicTrainingEffect")
    load = a.get("activityTrainingLoad")
    avg_hr = a.get("averageHR")
    max_hr = a.get("maxHR")
    print(f"{st} | {tkey:<18} | Dist: {dist:5.2f}km | Dur: {dur:5.1f}m | AvgHR: {avg_hr} | MaxHR: {max_hr} | Aerobic TE: {te} | Load: {load}")
