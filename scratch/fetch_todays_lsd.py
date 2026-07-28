import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

activity_id = "23475268160"
print(f"=== DEEP DIVE: Run {activity_id} ===\n")

# Full activity details
details = client.get_activity(activity_id)
print(f"Name: {details.get('activityName')}")
print(f"Date: {details.get('startTimeLocal')}")
print(f"Distance: {details.get('distance', 0)/1000:.2f} km")
print(f"Duration: {details.get('duration', 0)/60:.1f} min")
print(f"Avg Pace: {details.get('averageSpeed', 0)}")
print(f"Avg HR: {details.get('averageHR')} bpm | Max HR: {details.get('maxHR')} bpm")
print(f"Aerobic TE: {details.get('aerobicTrainingEffect')}")
print(f"Anaerobic TE: {details.get('anaerobicTrainingEffect')}")
print(f"Calories: {details.get('calories')} kcal")
print(f"Avg Cadence: {details.get('averageRunningCadenceInStepsPerMinute')} spm")
print(f"Avg Stride Length: {details.get('avgStrideLength')} m")
print(f"Vertical Oscillation: {details.get('avgVerticalOscillation')} cm")
print(f"Ground Contact Time: {details.get('avgGroundContactTime')} ms")
print(f"Vertical Ratio: {details.get('avgVerticalRatio')} %")
print(f"Training Load: {details.get('activityTrainingLoad')}")
print(f"EPOC: {details.get('epoc')}")
print(f"Recovery Time: {details.get('recoveryTime')} hours")
print()

# Lap-by-lap breakdown
splits = client.get_activity_splits(activity_id)
print("=== LAP-BY-LAP BREAKDOWN ===")
laps = splits.get("lapDTOs", [])
for i, lap in enumerate(laps, 1):
    dist = lap.get("distance", 0) / 1000
    pace_mps = lap.get("averageSpeed", 0)
    if pace_mps and pace_mps > 0:
        pace_sec = 1000 / pace_mps
        pace_min = int(pace_sec // 60)
        pace_s = int(pace_sec % 60)
        pace_str = f"{pace_min}:{pace_s:02d}/km"
    else:
        pace_str = "N/A"
    avg_hr = lap.get("averageHR", 0)
    max_hr = lap.get("maxHR", 0)
    cadence = lap.get("averageRunCadence", 0)
    print(f"  Km {i:>2}: {dist:.2f} km | {pace_str} | Avg HR: {avg_hr} | Max HR: {max_hr} | Cadence: {cadence} spm")
