"""
fetch_vitals_jul29.py
Fetches the morning vitals (HRV, Sleep, Body Battery, RHR) for July 29 to enforce Rule 2.
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

today = date(2026, 7, 29).isoformat()

print(f"=== VITALS FOR {today} ===")
try:
    sleep = client.get_sleep_data(today)
    sleep_score = sleep.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value', 'N/A')
    print(f"Sleep Score: {sleep_score}")
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

try:
    bb = client.get_body_battery(today)
    if bb:
        # Get highest BB value for the day so far
        bb_vals = [x['bodyBatteryValue'] for x in bb if 'bodyBatteryValue' in x]
        max_bb = max(bb_vals) if bb_vals else 'N/A'
        print(f"Body Battery (Peak): {max_bb}")
except:
    print("Body Battery: Failed to fetch")

try:
    trs = client.get_training_readiness(today)
    trs_score = trs.get('readiness', 'N/A')
    print(f"Training Readiness: {trs_score}")
except:
    print("Training Readiness: Failed to fetch")
