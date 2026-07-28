import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date
from garminconnect.workout import (
    BaseWorkout, WorkoutSegment, ExecutableStep, RepeatGroup, TargetType,
)

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_LAP_BUTTON = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}

def _no_target():
    return {"workoutTargetTypeId": TargetType.NO_TARGET, "workoutTargetTypeKey": "no.target"}

def _repeat(step_order, name, iterations):
    return RepeatGroup(
        stepOrder=step_order,
        stepType={"stepTypeId": 6, "stepTypeKey": "repeat"},
        numberOfIterations=iterations,
        workoutSteps=[
            ExecutableStep(
                stepOrder=1,
                stepType={"stepTypeId": 3, "stepTypeKey": "interval"},
                endCondition=_LAP_BUTTON,
                targetType=_no_target(),
                description=name,
            ),
            ExecutableStep(
                stepOrder=2,
                stepType={"stepTypeId": 5, "stepTypeKey": "rest"},
                endCondition=_LAP_BUTTON,
                targetType=_no_target(),
                description="Rest (Lap to advance)",
            ),
        ],
    )

steps = []
i = 1

steps.append(_repeat(i, "Machine Chest Press (Wrist Straight)", 4)); i += 1
steps.append(_repeat(i, "Pec Deck / Machine Flyes", 4)); i += 1
steps.append(_repeat(i, "Cable Tricep Pushdowns (Rope or Straight Bar)", 4)); i += 1
steps.append(_repeat(i, "Overhead Cable Tricep Extensions", 3)); i += 1

workout = BaseWorkout(
    workoutName="Push — Wrist Safe (Chest & Triceps)",
    description=(
        "Wrist-safe Push session for July 7. "
        "Keep wrists stacked on press. Machine flyes load forearms. "
        "Cable pushdowns and extensions keep wrists locked."
    ),
    estimatedDurationInSecs=2400,
    sportType={"sportTypeId": 5, "sportTypeKey": "strength_training"},
    workoutSegments=[
        WorkoutSegment(
            segmentOrder=1,
            sportType={"sportTypeId": 5, "sportTypeKey": "strength_training"},
            workoutSteps=steps,
        )
    ],
)

target_date = date.today().isoformat()
print(f"Uploading Push Day workout for {target_date}...")
res = client.upload_workout(workout.model_dump())
workout_id = res.get("workoutId")
print(f"Uploaded! Workout ID: {workout_id}")
client.schedule_workout(workout_id, target_date)
print(f"Scheduled on Garmin for {target_date}!")
print()
print("Session breakdown:")
print("  Machine Chest Press                — 4 sets")
print("  Pec Deck / Machine Flyes           — 4 sets")
print("  Cable Tricep Pushdowns             — 4 sets")
print("  Overhead Cable Tricep Extensions   — 3 sets")
print("  TOTAL: 15 working sets | ~35-40 min")
