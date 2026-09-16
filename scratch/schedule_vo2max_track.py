"""
schedule_vo2max_track.py
Schedules a 6x400m VO2 Max track workout with Lap Button warmups.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from garminconnect.workout import (
    RunningWorkout, WorkoutSegment, ExecutableStep, RepeatGroup,
    StepType, ConditionType, TargetType
)

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

workout_name = "VO2 Max 6x400m (Track)"
notes = "Warmup to the track (hit lap when you arrive). 6x400m Z5 sprints with 90s walk recovery. Cooldown jog home (hit lap to end)."

seg = WorkoutSegment(segmentOrder=1)
step_order = 1

# 1. Warmup (Lap Button)
warmup = ExecutableStep(
    stepOrder=step_order,
    stepType={"stepTypeId": StepType.WARMUP, "stepTypeKey": "warmup", "displayOrder": 1},
    endCondition={"conditionTypeId": ConditionType.LAP_BUTTON, "conditionTypeKey": "lap.button", "displayOrder": 1},
    endConditionValue=None,
    targetType={"workoutTargetTypeId": TargetType.HEART_RATE_ZONE, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
    targetValueOne=1,
    targetValueTwo=2
)
seg.add_step(warmup)
step_order += 1

# 2. Intervals (Repeat Group)
repeats = RepeatGroup(stepOrder=step_order, numberOfIterations=6)
# 400m sprint
interval = ExecutableStep(
    stepOrder=1,
    stepType={"stepTypeId": StepType.INTERVAL, "stepTypeKey": "interval", "displayOrder": 3},
    endCondition={"conditionTypeId": ConditionType.DISTANCE, "conditionTypeKey": "distance", "displayOrder": 3},
    endConditionValue=400, # meters
    targetType={"workoutTargetTypeId": TargetType.HEART_RATE_ZONE, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
    targetValueOne=5,
    targetValueTwo=5
)
repeats.add_step(interval)

# 90s recovery
recovery = ExecutableStep(
    stepOrder=2,
    stepType={"stepTypeId": StepType.RECOVERY, "stepTypeKey": "recovery", "displayOrder": 4},
    endCondition={"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time", "displayOrder": 2},
    endConditionValue=90, # seconds
    targetType={"workoutTargetTypeId": TargetType.HEART_RATE_ZONE, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
    targetValueOne=1,
    targetValueTwo=1
)
repeats.add_step(recovery)

seg.add_step(repeats)
step_order += 1

# 3. Cooldown (Lap Button)
cooldown = ExecutableStep(
    stepOrder=step_order,
    stepType={"stepTypeId": StepType.COOLDOWN, "stepTypeKey": "cooldown", "displayOrder": 2},
    endCondition={"conditionTypeId": ConditionType.LAP_BUTTON, "conditionTypeKey": "lap.button", "displayOrder": 1},
    endConditionValue=None,
    targetType={"workoutTargetTypeId": TargetType.HEART_RATE_ZONE, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
    targetValueOne=1,
    targetValueTwo=2
)
seg.add_step(cooldown)

workout = RunningWorkout(
    workoutName=workout_name,
    estimatedDurationInSecs=3600,
    workoutSegments=[seg]
)
workout.description = notes

try:
    print(f"Creating workout: {workout_name}...")
    result = client.upload_running_workout(workout)
    workout_id = result.get('workoutId')
    print(f"Workout uploaded with ID: {workout_id}")
    
    today = date(2026, 7, 30).isoformat()
    client.schedule_workout(workout_id, today)
    print(f"Workout successfully scheduled for {today}")
except Exception as e:
    print(f"Failed to schedule workout: {e}")
