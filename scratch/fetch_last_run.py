"""
fetch_last_run.py
Pulls the latest run activity and its lap data to analyze the user's 45-min override.
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

acts = client.get_activities(0, 5)
latest_run = None
for a in acts:
    if a.get('activityType', {}).get('typeKey', '') == 'running':
        latest_run = a
        break

if not latest_run:
    print("No running activity found.")
    sys.exit()

act_id = latest_run.get('activityId')
name = latest_run.get('activityName', 'Unknown')
dist = (latest_run.get('distance', 0)) / 1000.0
dur = (latest_run.get('duration', 0)) / 60.0
avg_hr = latest_run.get('averageHR')
max_hr = latest_run.get('maxHR')
ae = latest_run.get('aerobicTrainingEffect')
an = latest_run.get('anaerobicTrainingEffect')
cadence = latest_run.get('averageRunningCadenceInStepsPerMinute')
stride = latest_run.get('avgStrideLength')

print(f"=== {name} ===")
print(f"Distance: {dist:.2f} km")
print(f"Duration: {dur:.1f} mins")
print(f"HR: Avg {avg_hr} / Max {max_hr}")
print(f"TE: Ae {ae} / An {an}")
print(f"Cadence: {cadence} spm | Stride: {stride} cm")
print("-" * 30)

try:
    splits = client.get_activity_splits(act_id)
    lap_dtos = splits.get('lapDTOs', [])
    for i, lap in enumerate(lap_dtos):
        lap_dist = lap.get('distance', 0) / 1000.0
        lap_hr = lap.get('averageHR', 0)
        lap_max = lap.get('maxHR', 0)
        speed = lap.get('averageSpeed', 0)
        if speed > 0:
            pace = 1000 / speed / 60
            pace_str = f"{int(pace)}:{int((pace - int(pace)) * 60):02d}/km"
        else:
            pace_str = "N/A"
        print(f"Lap {i+1}: {lap_dist:.2f}km | Pace: {pace_str} | HR: {lap_hr}/{lap_max}")
except Exception as e:
    print(f"Error fetching laps: {e}")
