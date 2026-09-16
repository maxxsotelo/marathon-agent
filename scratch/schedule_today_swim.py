"""
schedule_today_swim.py
Schedules a 30-40 min Active Recovery Swim to Garmin Calendar.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from garminconnect.workout import (
    SwimmingWorkout,
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

workout_name = "Active Recovery Swim (Hydrostatic)"
desc = "Zone 1 Hydrostatic Flush. Max 1,500m. Use pull buoy if possible. DO NOT KICK HARD (Protect IT Band)."

# Step 1: Warmup
step1 = ExecutableStep(
    stepOrder=1,
    stepType={"stepTypeId": StepType.WARMUP, "stepTypeKey": "warmup", "displayOrder": 1},
    endCondition={"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
    endConditionValue=300, 
    targetType={"workoutTargetTypeId": TargetType.NO_TARGET, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
)

# Step 2: Main Body
step2 = ExecutableStep(
    stepOrder=2,
    stepType={"stepTypeId": StepType.INTERVAL, "stepTypeKey": "interval", "displayOrder": 3},
    endCondition={"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
    endConditionValue=1800,
    targetType={"workoutTargetTypeId": TargetType.NO_TARGET, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
)

# Step 3: Cooldown
step3 = ExecutableStep(
    stepOrder=3,
    stepType={"stepTypeId": StepType.COOLDOWN, "stepTypeKey": "cooldown", "displayOrder": 2},
    endCondition={"conditionTypeId": ConditionType.TIME, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
    endConditionValue=300,
    targetType={"workoutTargetTypeId": TargetType.NO_TARGET, "workoutTargetTypeKey": "no.target", "displayOrder": 1}
)

workout = SwimmingWorkout(
    workoutName=workout_name,
    description=desc,
    estimatedDurationInSecs=2400,
    workoutSegments=[
        WorkoutSegment(
            segmentOrder=1,
            sportType={
                "sportTypeId": SportType.SWIMMING,
                "sportTypeKey": "swimming",
            },
            workoutSteps=[step1, step2, step3]
        )
    ],
    poolLength=25,
    poolLengthUnit="meter"
)

try:
    print(f"Uploading {workout_name}...")
    result = client.upload_swimming_workout(workout)
    workout_id = result.get("workoutId")
    if workout_id:
        print(f"Uploaded! ID: {workout_id}")
        today = date(2026, 8, 11).isoformat()
        client.schedule_workout(workout_id, today)
        print(f"Scheduled for {today}.")
    else:
        print("Upload failed.")
except Exception as e:
    print(f"Failed: {e}")
