import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}

workout = {
    "workoutName": "Legs + Core (Pre-Fatigue)",
    "description": "Pre-Fatigue Protocol for tomorrow's 21km. Heavy Leg Press, single-leg, and mandatory 4x20 Seated Calf Raises (70kg).",
    "sportType": {"sportTypeId": 9, "sportTypeKey": "strength_training"},
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 9, "sportTypeKey": "strength_training"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Warmup (Press LAP to advance)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Leg Press (Heavy 100kg+)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Single-Leg Press (46kg)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 4,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Seated Calf Raises (4x20 @ 70kg, 3s eccentric) - ACHILLES"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 5,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Hamstring Curls / GHD"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 6,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Core (Planks, Rollouts)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 7,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Stretch (Press LAP to end)"
                }
            ]
        }
    ]
}

today = date.today().isoformat()
try:
    res = client.upload_workout(workout)
    workout_id = res.get("workoutId")
    client.schedule_workout(workout_id, today)
    print("Scheduled Pre-Fatigue Legs successfully.")
except Exception as e:
    print(f"Error: {e}")
