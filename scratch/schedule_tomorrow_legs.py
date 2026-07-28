import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta
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

# LEGS
steps.append(_repeat(i, "Leg Press or Hack Squat (Heavy, Controlled)", 4)); i += 1
steps.append(_repeat(i, "Bulgarian Split Squats (DBs neutral grip)", 3)); i += 1
steps.append(_repeat(i, "Seated or Lying Leg Curls (Hamstrings)", 4)); i += 1
steps.append(_repeat(i, "Seated Calf Raises (Achilles Bulletproof 4x20)", 4)); i += 1

# CORE
steps.append(_repeat(i, "Weighted Planks (20kg)", 3)); i += 1
steps.append(_repeat(i, "Ab Rollouts (15kg or bodyweight)", 3)); i += 1

workout = BaseWorkout(
    workoutName="Legs + Core (Base Building)",
    description=(
        "Leg day for July 8. Heavy slow resistance to build structural durability. "
        "No explosive plyometrics. Focus on controlled eccentrics. "
        "Includes mandatory Achilles bulletproofing."
    ),
    estimatedDurationInSecs=2700,
    sportType={"sportTypeId": 5, "sportTypeKey": "strength_training"},
    workoutSegments=[
        WorkoutSegment(
            segmentOrder=1,
            sportType={"sportTypeId": 5, "sportTypeKey": "strength_training"},
            workoutSteps=steps,
        )
    ],
)

target_date = (date.today() + timedelta(days=1)).isoformat()
print(f"Uploading Leg Day workout for {target_date}...")
res = client.upload_workout(workout.model_dump())
workout_id = res.get("workoutId")
print(f"Uploaded! Workout ID: {workout_id}")
client.schedule_workout(workout_id, target_date)
print(f"Scheduled on Garmin for {target_date}!")
print()
print("Session breakdown:")
print("  Leg Press / Hack Squat                 — 4 sets")
print("  Bulgarian Split Squats                 — 3 sets")
print("  Leg Curls (Hamstrings)                 — 4 sets")
print("  Seated Calf Raises (4x20 Achilles)     — 4 sets")
print("  Weighted Planks                        — 3 sets")
print("  Ab Rollouts                            — 3 sets")
print("  TOTAL: 21 working sets | ~45 min")
