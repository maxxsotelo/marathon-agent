import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()

print(f"=== Vitals for {today} ===")
try:
    stats = client.get_stats(today)
    rhr = stats.get("restingHeartRate")
    print(f"Resting HR: {rhr} bpm")
except Exception as e:
    print(f"Resting HR: Error fetching - {e}")

try:
    bb = client.get_body_battery(today)
    latest_bb = None
    if bb and isinstance(bb, list) and len(bb) > 0:
        values = bb[0].get("bodyBatteryValuesArray", [])
        if values:
            latest_bb = values[-1][1]
    print(f"Current Body Battery: {latest_bb}")
except Exception as e:
    print(f"Body Battery: Error fetching - {e}")

try:
    sleep = client.get_sleep_data(today)
    sleep_score = sleep.get("dailySleepDTO", {}).get("sleepScore", "N/A")
    sleep_dur = sleep.get("dailySleepDTO", {}).get("sleepTimeSeconds", 0) // 60
    print(f"Sleep Score: {sleep_score}")
    print(f"Sleep Duration: {sleep_dur // 60}h {sleep_dur % 60}m")
except Exception as e:
    print(f"Sleep: Error fetching - {e}")

try:
    hrv = client.get_hrv_data(today)
    hrv_val = hrv.get("hrvSummary", {}).get("lastNightAvg", "N/A")
    hrv_status = hrv.get("hrvSummary", {}).get("status", "N/A")
    print(f"Last Night HRV: {hrv_val} ms ({hrv_status})")
except Exception as e:
    print(f"HRV: Error fetching - {e}")
