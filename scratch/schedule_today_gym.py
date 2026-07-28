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

# VERTICAL PULL
steps.append(_repeat(i, "Lat Pulldown (Wide Grip)", 4)); i += 1
steps.append(_repeat(i, "Single-Arm Cable Pulldown / Straight-Arm Pulldown", 3)); i += 1

# HORIZONTAL PULL
steps.append(_repeat(i, "Seated Cable Row (Neutral Grip)", 4)); i += 1
steps.append(_repeat(i, "Cable Chest-Supported Row / Machine Row", 3)); i += 1

# REAR DELT + ROTATOR CUFF
steps.append(_repeat(i, "Rear Delt Cable Flyes (Face Down or Standing)", 3)); i += 1
steps.append(_repeat(i, "Face Pulls — External Rotation Focus", 3)); i += 1

# BICEPS
steps.append(_repeat(i, "Hammer Curls (DB) or Cable Curl", 3)); i += 1

workout = BaseWorkout(
    workoutName="Pull Day — Back, Rear Delt, Biceps (Wrist-Safe)",
    description=(
        "Week 3 Pull Session. Vertical Pull: Lat Pulldown 4x, Straight-Arm Pulldown 3x. "
        "Horizontal Pull: Cable Row 4x, Machine Row 3x. "
        "Rear Delt/Rotator: Rear Delt Flyes 3x, Face Pulls 3x. "
        "Biceps: Hammer Curls 3x. All wrist-safe — no pronated barbell curls."
    ),
    estimatedDurationInSecs=3000,
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
print(f"Uploading Pull Day workout for {target_date}...")
res = client.upload_workout(workout.model_dump())
workout_id = res.get("workoutId")
print(f"Uploaded! Workout ID: {workout_id}")
client.schedule_workout(workout_id, target_date)
print(f"Scheduled on Garmin for {target_date}!")
print()
print("Session breakdown:")
print("  Lat Pulldown (Wide Grip)              — 4 sets")
print("  Straight-Arm Cable Pulldown           — 3 sets")
print("  Seated Cable Row (Neutral Grip)       — 4 sets")
print("  Cable / Machine Row                   — 3 sets")
print("  Rear Delt Cable Flyes                 — 3 sets")
print("  Face Pulls (External Rotation)        — 3 sets")
print("  Hammer Curls / Cable Curl             — 3 sets")
print("  TOTAL: 23 working sets | ~50 min")
