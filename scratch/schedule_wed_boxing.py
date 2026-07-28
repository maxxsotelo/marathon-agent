import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Tomorrow's date
tomorrow = (date.today() + timedelta(days=1)).isoformat()

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}

workout = {
    "workoutName": "Boxing + Upper Body (Tech & Tone)",
    "description": "Week 5 Day 2. Focus on technique, speed, and a moderate upper body pump. DO NOT go to muscular failure. Save the CNS for tomorrow's threshold runs.",
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
                    "description": "Warmup (Jump rope / dynamic stretching)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Boxing: Technical Shadowboxing / Light Bag Work"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Upper Body Gym: Shoulders, Chest, Back (Moderate weight, NO FAILURE)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 4,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Cooldown & Core"
                }
            ]
        }
    ]
}

try:
    res = client.upload_workout(workout)
    wid = res.get("workoutId")
    client.schedule_workout(wid, tomorrow)
    print(f"[OK] Scheduled: {workout['workoutName']} for {tomorrow}")
except Exception as e:
    print(f"[ERR] Error scheduling: {e}")
