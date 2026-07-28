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
    "workoutName": "Core + Shoulders Recovery",
    "description": "Active recovery for legs. Core focus (Planks, Rollouts, Twists) + Shoulder Isolation (Lateral raises). Keep HR low.",
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
                    "description": "Light Warmup / Mobility (Press LAP to end)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Core Circuit: Rollouts / Planks / Twists"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 5, "stepTypeKey": "rest"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Rest"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 4,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Shoulder Isolation: Lateral Raises / Arnold Press"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 5,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Stretch (Press LAP to save)"
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
    print("Scheduled Core + Shoulders successfully.")
except Exception as e:
    print(f"Error: {e}")
