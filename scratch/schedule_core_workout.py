import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date
from garminconnect.workout import (
    BaseWorkout,
    WorkoutSegment,
    ExecutableStep,
    SportType,
    StepType,
    ConditionType,
    TargetType,
)

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
)
client.login(TOKEN_STORE)

# Helpers
_STEP_TYPES = {
    "interval": {"stepTypeId": StepType.INTERVAL,  "stepTypeKey": "interval", "displayOrder": 3},
    "rest":     {"stepTypeId": 5,                  "stepTypeKey": "rest",     "displayOrder": 5},
}

_REPS_CONDITION = {
    "conditionTypeId": 10,
    "conditionTypeKey": "reps",
    "displayOrder": 10,
    "displayable": True,
}

_TIME_CONDITION = {
    "conditionTypeId": 2,
    "conditionTypeKey": "time",
    "displayOrder": 2,
    "displayable": True,
}

def _no_target_type():
    return {
        "workoutTargetTypeId": TargetType.NO_TARGET,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1,
    }

def _build_set(step_order: int, name: str, reps: int) -> ExecutableStep:
    return ExecutableStep(
        stepOrder=step_order,
        stepType=_STEP_TYPES["interval"],
        endCondition=_REPS_CONDITION,
        endConditionValue=float(reps),
        targetType=_no_target_type(),
        description=name,
    )

def _build_timed_set(step_order: int, name: str, duration_secs: float) -> ExecutableStep:
    return ExecutableStep(
        stepOrder=step_order,
        stepType=_STEP_TYPES["interval"],
        endCondition=_TIME_CONDITION,
        endConditionValue=duration_secs,
        targetType=_no_target_type(),
        description=name,
    )

def _build_rest(step_order: int, rest_secs: float) -> ExecutableStep:
    return ExecutableStep(
        stepOrder=step_order,
        stepType=_STEP_TYPES["rest"],
        endCondition=_TIME_CONDITION,
        endConditionValue=rest_secs,
        targetType=_no_target_type(),
        description=f"Rest {int(rest_secs)}s",
    )

# Build workout steps — 2 rounds of the 3 exercises
workout_steps = []
step_idx = 1

for round_num in range(1, 3):  # 2 rounds
    # 1. Dead Bugs — 10 reps/side = 20 total
    workout_steps.append(_build_set(step_idx, f"Dead Bugs - Round {round_num} (10 reps/side, lower back flat)", 20))
    step_idx += 1
    workout_steps.append(_build_rest(step_idx, 30.0))
    step_idx += 1

    # 2. Plank — 45 seconds
    workout_steps.append(_build_timed_set(step_idx, f"Plank - Round {round_num} (squeeze glutes + abs)", 45.0))
    step_idx += 1
    workout_steps.append(_build_rest(step_idx, 30.0))
    step_idx += 1

    # 3. Side Plank — 30 seconds per side
    workout_steps.append(_build_timed_set(step_idx, f"Side Plank - Round {round_num} (30 sec/side, hips up)", 60.0))
    step_idx += 1
    if round_num < 2:
        workout_steps.append(_build_rest(step_idx, 60.0))
        step_idx += 1

workout = BaseWorkout(
    workoutName="Core — Dead Bugs, Planks & Side Planks",
    description="2 Rounds | Isometric Core Stabilization. Dead Bugs 10/side, Plank 45s, Side Plank 30s/side.",
    estimatedDurationInSecs=600,
    sportType={
        "sportTypeId": 5,
        "sportTypeKey": "strength_training",
    },
    workoutSegments=[
        WorkoutSegment(
            segmentOrder=1,
            sportType={
                "sportTypeId": 5,
                "sportTypeKey": "strength_training",
            },
            workoutSteps=workout_steps,
        )
    ],
)

target_date = "2026-05-26"
print(f"Uploading Core Workout for {target_date}...")

try:
    res = client.upload_workout(workout.model_dump() if hasattr(workout, 'model_dump') else workout.dict())
    workout_id = res.get("workoutId")
    print(f"Workout uploaded! ID: {workout_id}")
    client.schedule_workout(workout_id, target_date)
    print(f"Scheduled on Garmin calendar for {target_date}!")
except Exception as e:
    print(f"Error: {e}")
