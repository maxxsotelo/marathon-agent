import os
from dotenv import load_dotenv
from garminconnect import Garmin
from datetime import date
import json

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser('~/.garminconnect')
client = Garmin(os.getenv('GARMIN_EMAIL'), os.getenv('GARMIN_PASSWORD'))
client.login(TOKEN_STORE)

today_str = "2026-09-21"

print("--- BODY BATTERY ---")
try:
    bb = client.get_body_battery(today_str)
    if bb and len(bb) > 0:
        latest = bb[-1]
        print(f"Charged: {latest.get('charged')}, Drained: {latest.get('drained')}, Current/Last: {latest.get('bodyBatteryValuesArray', [[]])[-1] if latest.get('bodyBatteryValuesArray') else 'N/A'}")
except Exception as e:
    print("BB error:", e)

print("--- SLEEP ---")
try:
    sleep = client.get_sleep_data(today_str)
    dto = sleep.get('dailySleepDTO', {})
    score = dto.get('sleepScores', {}).get('overall', {}).get('value')
    total_sec = dto.get('sleepTimeSeconds', 0)
    deep_sec = dto.get('deepSleepSeconds', 0)
    rem_sec = dto.get('remSleepSeconds', 0)
    print(f"Sleep Score: {score} | Duration: {total_sec/3600:.2f}h ({total_sec/60:.0f}m) | Deep: {deep_sec/60:.0f}m | REM: {rem_sec/60:.0f}m")
except Exception as e:
    print("Sleep error:", e)

print("--- HRV ---")
try:
    hrv = client.get_hrv_data(today_str)
    summary = hrv.get('hrvSummary', {})
    print(f"Last Night Avg: {summary.get('lastNightAvg')} ms | Status: {summary.get('status')} | Baseline: {summary.get('baseline')}")
except Exception as e:
    print("HRV error:", e)

print("--- RHR ---")
try:
    rhr_data = client.get_rhr_day(today_str)
    metrics = rhr_data.get('allMetrics', {}).get('metricsMap', {})
    print("RHR metrics:", metrics)
except Exception as e:
    print("RHR error:", e)

print("--- TRAINING READINESS / STATUS ---")
try:
    ts = client.get_training_status(today_str)
    print("Training Status keys:", list(ts.keys()) if isinstance(ts, dict) else type(ts))
    for k, v in ts.items():
        if 'phrase' in str(k).lower() or 'load' in str(k).lower() or 'status' in str(k).lower() or 'recovery' in str(k).lower():
            print(f"  {k}: {v}")
except Exception as e:
    print("Training status error:", e)

