"""
fetch_run_deep_telemetry_aug6.py
Deep telemetry for the August 6 threshold run.
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

today = date(2026, 8, 6).isoformat()
activities = client.get_activities_by_date(today, today)

# Find the main running activity
run_act = None
for act in activities:
    if act.get('activityName') == 'To the track and the tempo/threshold session':
        run_act = act
        break

if not run_act:
    print("Main activity not found.")
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
    avg_speed = summary.get('averageSpeed', 0)
    if avg_speed and avg_speed > 0:
        avg_pace_min = (1000 / avg_speed) / 60
        pace_min = int(avg_pace_min)
        pace_sec = int((avg_pace_min - pace_min) * 60)
        print(f"  Avg Pace: {pace_min}:{pace_sec:02d} /km")
    print(f"  Avg Cadence: {summary.get('averageRunCadence')} spm")
    print(f"  Avg Stride Length: {summary.get('averageStrideLength')} m")
    print(f"  Training Effect: Ae {details.get('aerobicTrainingEffect')} / An {details.get('anaerobicTrainingEffect')}")
    print(f"  VO2Max Estimate: {summary.get('vO2MaxValue')}")
    print(f"  Calories: {summary.get('calories')}")
    print()
except Exception as e:
    print(f"Details failed: {e}")

# 2. Lap-by-lap breakdown
try:
    splits = client.get_activity_splits(act_id)
    laps = splits.get('lapDTOs', [])
    print("=== LAP BREAKDOWN ===")
    for i, lap in enumerate(laps, 1):
        lap_dist = lap.get('distance', 0) / 1000
        lap_dur  = lap.get('duration', 0) / 60
        lap_hr   = lap.get('averageHR', 0)
        lap_maxhr = lap.get('maxHR', 0)
        spd = lap.get('averageSpeed', 0)
        if spd and spd > 0:
            pm = (1000 / spd) / 60
            p_m = int(pm); p_s = int((pm - p_m) * 60)
            pace_str = f"{p_m}:{p_s:02d}/km"
        else:
            pace_str = "N/A"
        print(f"  Lap {i:2d}: {lap_dist:.2f}km | {pace_str} | HR avg {lap_hr} / max {lap_maxhr}")
    print()
except Exception as e:
    print(f"Laps failed: {e}")

# 3. HR zones
try:
    zones = client.get_activity_hr_in_timezones(act_id)
    print("=== TIME IN HR ZONES ===")
    for zone in zones:
        z_num  = zone.get('zoneNumber', '?')
        z_secs = zone.get('secsInZone', 0)
        z_min  = z_secs / 60
        z_pct  = zone.get('zonePercentage', 0)
        print(f"  Zone {z_num}: {z_min:.1f} mins ({z_pct:.1f}%)")
    print()
except Exception as e:
    print(f"HR zones failed: {e}")
