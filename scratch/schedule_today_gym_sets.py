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
    RepeatGroup,
    TargetType,
)

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Helpers
_LAP_BUTTON = {
    "conditionTypeId": 1,
    "conditionTypeKey": "lap.button",
}

def _no_target():
    return {
        "workoutTargetTypeId": TargetType.NO_TARGET,
        "workoutTargetTypeKey": "no.target",
    }

def _build_set(step_order: int, name: str) -> ExecutableStep:
    return ExecutableStep(
        stepOrder=step_order,
        stepType={"stepTypeId": 3, "stepTypeKey": "interval"},
        endCondition=_LAP_BUTTON,
        targetType=_no_target(),
        description=name,
    )

def _build_rest(step_order: int) -> ExecutableStep:
    return ExecutableStep(
        stepOrder=step_order,
        stepType={"stepTypeId": 5, "stepTypeKey": "rest"},
        endCondition=_LAP_BUTTON,
        targetType=_no_target(),
        description="Rest (Lap to advance)",
    )

def _build_repeat_group(step_order: int, name: str, iterations: int) -> RepeatGroup:
    # A repeat group contains 1 active set + 1 rest set inside it.
    # The inner step orders don't matter as much, but we'll set them to 1 and 2.
    steps = [
        _build_set(1, name),
        _build_rest(2)
    ]
    return RepeatGroup(
        stepOrder=step_order,
        stepType={"stepTypeId": 6, "stepTypeKey": "repeat"},
        numberOfIterations=iterations,
        workoutSteps=steps,
    )

workout_steps = []
step_idx = 1

# 1. Pull-Ups
workout_steps.append(_build_repeat_group(step_idx, "Pull-Ups (or Assisted)", 4))
step_idx += 1

# 2. Rows
workout_steps.append(_build_repeat_group(step_idx, "Seated Cable / DB Rows", 4))
step_idx += 1

# 3. Biceps
workout_steps.append(_build_repeat_group(step_idx, "Bicep/Hammer Curls", 3))
step_idx += 1

# 4. Core Circuit
workout_steps.append(_build_repeat_group(step_idx, "Core Circuit (Leg Raises, Planks, Rollouts)", 3))
step_idx += 1

workout = BaseWorkout(
    workoutName="Upper Body Pull + Core (Grouped)",
    description="Pull-Ups (4x), Rows (4x), Biceps (3x), Core Circuit (3x). Uses Garmin Sets Feature.",
    estimatedDurationInSecs=3600,
    sportType={"sportTypeId": 5, "sportTypeKey": "strength_training"},
    workoutSegments=[
        WorkoutSegment(
            segmentOrder=1,
            sportType={"sportTypeId": 5, "sportTypeKey": "strength_training"},
            workoutSteps=workout_steps,
        )
    ],
)

target_date = date.today().isoformat()
print(f"Uploading Grouped Workout for {target_date}...")

try:
    res = client.upload_workout(workout.model_dump() if hasattr(workout, 'model_dump') else workout.dict())
    workout_id = res.get("workoutId")
    print(f"Workout uploaded! ID: {workout_id}")
    client.schedule_workout(workout_id, target_date)
    print(f"Scheduled on Garmin calendar for {target_date}!")
except Exception as e:
    print(f"Error: {e}")
