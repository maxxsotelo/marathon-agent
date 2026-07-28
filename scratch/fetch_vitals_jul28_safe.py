"""
fetch_vitals_jul28_safe.py
Fetches morning vitals safely
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 28).isoformat()

print(f"=== VITALS FOR {today} ===")

try:
    summary = client.get_user_summary(today)
    print(f"Body Battery: {summary.get('bodyBatteryMostRecentValue', 'N/A')}/100")
    print(f"Resting HR: {summary.get('restingHeartRate', 'N/A')} bpm")
    print(f"Stress Score: {summary.get('averageStressLevel', 'N/A')}")
except Exception as e:
    print(f"Error summary: {e}")

try:
    hrv = client.get_hrv_data(today)
    if hrv:
        print(f"HRV Status: {hrv.get('hrvSummary', {}).get('status', 'N/A')}")
        print(f"HRV Last Night: {hrv.get('hrvSummary', {}).get('lastNightAvg', 'N/A')} ms")
        print(f"HRV Weekly Avg: {hrv.get('hrvSummary', {}).get('weeklyAvg', 'N/A')} ms")
except Exception as e:
    print(f"Error hrv: {e}")

try:
    sleep = client.get_sleep_data(today)
    if sleep:
        score = sleep.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value', 'N/A')
        secs = sleep.get('dailySleepDTO', {}).get('sleepTimeSeconds', None)
        print(f"Sleep Score: {score}/100")
        if secs:
            print(f"Sleep Time: {secs // 3600}h {(secs % 3600) // 60}m")
        else:
            print("Sleep Time: N/A")
except Exception as e:
    print(f"Error sleep: {e}")

try:
    readiness = client.get_training_readiness(today)
    if readiness:
        print(f"Training Readiness: {readiness.get('readinessScore', 'N/A')}/100")
        print(f"Recovery Time: {readiness.get('recoveryTime', 'N/A')} hours")
except Exception as e:
    print(f"Error readiness: {e}")
