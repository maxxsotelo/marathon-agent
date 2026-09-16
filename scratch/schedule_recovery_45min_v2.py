"""
schedule_recovery_45min_v2.py
Schedules a 45-minute time-based recovery run to Garmin Connect for today using garminconnect.workout module.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from garminconnect.workout import (
    RunningWorkout,
    WorkoutSegment,
    ExecutableStep,
    SportType,
    StepType,
    ConditionType,
    TargetType
)

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

workout_name = "Recovery Flush (45m)"
workout_notes = "Engine Note: User override accepted. Mechanical ACWR clears this load (0.947). Keep HR strictly in Zone 1 / low Zone 2 to preserve glycogen for Thursday's VO2 Max."

# Build workout
workout = RunningWorkout(workout_name)
workout.description = workout_notes

seg = WorkoutSegment(1)

# Active step for 45 minutes targeting HR zone 1-2
step = ExecutableStep(1)
step.step_type = StepType.active
step.end_condition = ConditionType.time
step.end_condition_value = 45 * 60 # seconds
step.target_type = TargetType.heart_rate_zone
step.target_value_one = 1
step.target_value_two = 2

seg.add_step(step)
workout.add_segment(seg)

try:
    print(f"Creating workout: {workout_name}...")
    workout_payload = workout.create_workout_payload()
    created = client.save_workout(workout_payload)
    workout_id = created.get("workoutId")
    print(f"Workout created with ID: {workout_id}")
    
    today = date(2026, 7, 28).isoformat()
    client.schedule_workout(workout_id, today)
    print(f"Workout successfully scheduled for {today}")
except Exception as e:
    print(f"Failed to schedule workout: {e}")
