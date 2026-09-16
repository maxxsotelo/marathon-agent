"""
schedule_vo2max_track_easy.py
Schedules a 6x400m VO2 Max track workout by modifying the generator's output.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from actuator_workout_generator import create_workout

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

workout = create_workout("intervals", 50, "vo2max", "run")
workout.workoutName = "VO2 Max 6x400m (Track)"
workout.description = "Warmup to the track (hit lap when you arrive). 6x400m Z5 sprints with 90s walk recovery. Cooldown jog home (hit lap to end)."

steps = workout.workoutSegments[0].workoutSteps
warmup_step = steps[0]
warmup_step.endCondition = {
    "conditionTypeId": 1, # Lap Button
    "conditionTypeKey": "lap.button",
    "displayOrder": 1,
    "displayable": True
}
warmup_step.endConditionValue = None

cooldown_step = steps[-1]
cooldown_step.endCondition = {
    "conditionTypeId": 1, # Lap Button
    "conditionTypeKey": "lap.button",
    "displayOrder": 1,
    "displayable": True
}
cooldown_step.endConditionValue = None

# Set intervals to 400m (default was 800) and repeats to 6
repeat_group = steps[1]
repeat_group.numberOfIterations = 6
if hasattr(repeat_group, 'workoutSteps'):
    interval_step = repeat_group.workoutSteps[0]
    interval_step.endConditionValue = 400 # 400m
    
    # 90s recovery
    rec_step = repeat_group.workoutSteps[1]
    rec_step.endConditionValue = 90

try:
    print(f"Uploading workout: {workout.workoutName}...")
    result = client.upload_running_workout(workout)
    workout_id = result.get('workoutId')
    print(f"Workout uploaded with ID: {workout_id}")
    
    today = date(2026, 7, 30).isoformat()
    client.schedule_workout(workout_id, today)
    print(f"Workout successfully scheduled for {today}")
except Exception as e:
    print(f"Failed to schedule workout: {e}")
