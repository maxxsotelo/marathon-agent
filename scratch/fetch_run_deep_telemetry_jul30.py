"""
fetch_run_deep_telemetry_jul30.py
Fetches the deep telemetry for the Jul 30 track session.
"""
import os, sys, json
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 30).isoformat()
activities = client.get_activities_by_date(today, today)

# Find the running activity
run_act = None
for act in activities:
    if 'running' in act.get('activityType', {}).get('typeKey', '').lower():
        run_act = act
        break

if not run_act:
    print("No running activity found.")
    exit()

act_id = run_act.get('activityId')
print(f"Run Activity ID: {act_id}")
print(f"Name: {run_act.get('activityName')}")
print()

# 1. Activity details
try:
    details = client.get_activity(act_id)
    summary = details.get('summaryDTO', {})
    print("=== SUMMARY ===")
    print(f"  Distance: {summary.get('distance', 0)/1000:.2f} km")
    print(f"  Duration: {summary.get('elapsedDuration', 0)/60:.1f} mins")
    print(f"  Avg HR: {summary.get('averageHR')} | Max HR: {summary.get('maxHR')}")
    print(f"  Avg Pace: {summary.get('averageSpeed', 0)} m/s")
    print(f"  Avg Cadence: {summary.get('averageRunCadence')} spm")
    print(f"  Avg Stride Length: {summary.get('averageStrideLength')} m")
    print(f"  Vertical Oscillation: {summary.get('averageVerticalOscillation')} cm")
    print(f"  GCT: {summary.get('averageGroundContactTime')} ms")
    print(f"  Vertical Ratio: {summary.get('averageVerticalRatio')}%")
    print(f"  Power: {summary.get('avgPower')} W")
    print(f"  Training Effect: Ae {details.get('aerobicTrainingEffect')} / An {details.get('anaerobicTrainingEffect')}")
    print(f"  VO2Max Estimate: {summary.get('vO2MaxValue')}")
    print(f"  Calories: {summary.get('calories')}")
    print()
except Exception as e:
    print(f"Details failed: {e}")

# 2. HR zones
try:
    zones = client.get_activity_hr_in_timezones(act_id)
    print("=== TIME IN HR ZONES ===")
    for zone in zones:
        z_num = zone.get('zoneNumber', '?')
        z_secs = zone.get('secsInZone', 0)
        z_min = z_secs / 60
        z_pct = zone.get('zonePercentage', 0)
        print(f"  Zone {z_num}: {z_min:.1f} mins ({z_pct:.1f}%)")
    print()
except Exception as e:
    print(f"HR zones failed: {e}")

# 3. Weather conditions during run
try:
    weather = client.get_activity_weather(act_id)
    print("=== WEATHER DURING RUN ===")
    temp = weather.get('temperatureInCelcius', weather.get('temperature', 'N/A'))
    humidity = weather.get('relativeHumidity', 'N/A')
    feels = weather.get('apparentTemperatureInCelcius', weather.get('apparentTemperature', 'N/A'))
    print(f"  Temp: {temp}°C | Feels Like: {feels}°C | Humidity: {humidity}%")
    print()
except Exception as e:
    print(f"Weather failed: {e}")

# 4. Performance condition
try:
    perf = client.get_activity_running_analyses(act_id)
    print("=== PERFORMANCE CONDITION ===")
    print(json.dumps(perf, indent=2)[:2000])
    print()
except Exception as e:
    print(f"Perf condition failed: {e}")
