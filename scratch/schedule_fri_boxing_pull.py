import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}

workout = {
    "workoutName": "Light Boxing + Pull (Back/Biceps)",
    "description": "CNS Protection Day. Boxing: Technical work only, no high-HR rounds. Pull: High reps (12-15), no failure sets. Balance the anterior boxing work with rear delts and lats.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "training"},
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 5, "sportTypeKey": "training"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Warmup (Dynamic stretching)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Boxing: Shadowboxing / Light Bag Work"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Pull Gym: Lat Pulldowns, Machine Rows, Face Pulls"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 4,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Arms: Bicep Curls (12-15 reps, no failure)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 5,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Cooldown (Press LAP to finish)"
                }
            ]
        }
    ]
}

try:
    res = client.upload_workout(workout)
    wid = res.get("workoutId")
    client.schedule_workout(wid, today)
    print(f"[OK] Scheduled: {workout['workoutName']} for {today}")
except Exception as e:
    print(f"[ERR] Error scheduling: {e}")
