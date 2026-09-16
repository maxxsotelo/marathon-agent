"""
fetch_vitals_today.py
Fetches the morning vitals (HRV, Sleep, Body Battery, RHR) for the current day to enforce Rule 2.
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

today = date.today().isoformat()

print(f"=== VITALS FOR {today} ===")
try:
    sleep = client.get_sleep_data(today)
    daily_sleep = sleep.get('dailySleepDTO', {})
    sleep_score = daily_sleep.get('sleepScores', {}).get('overall', {}).get('value', 'N/A')
    duration_seconds = daily_sleep.get('sleepTimeSeconds', 0)
    duration_hours = duration_seconds / 3600.0
    print(f"Sleep Score: {sleep_score} ({duration_hours:.2f} hours)")
except:
    print("Sleep: Failed to fetch")

try:
    hrv = client.get_hrv_data(today)
    hrv_val = hrv.get('hrvSummary', {}).get('weeklyAvg', 'N/A')
    hrv_last = hrv.get('hrvSummary', {}).get('lastNightAvg', 'N/A')
    print(f"HRV (7d Avg): {hrv_val} ms")
    print(f"HRV (Last Night): {hrv_last} ms")
except:
    print("HRV: Failed to fetch")

try:
    rhr_data = client.get_rhr_day(today)
    rhr_val = rhr_data.get('restingHeartRate', 'N/A')
    if rhr_val == 'N/A' and 'allMetrics' in rhr_data and len(rhr_data['allMetrics']['metricsMap']['WELLNESS_RESTING_HEART_RATE']) > 0:
        rhr_val = rhr_data['allMetrics']['metricsMap']['WELLNESS_RESTING_HEART_RATE'][0]['value']
    print(f"Resting HR: {rhr_val} bpm")
except:
    print("RHR: Failed to fetch")
