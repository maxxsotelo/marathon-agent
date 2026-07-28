import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}
_HR_TARGET_Z1 = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "targetValueOne": 1, "targetValueTwo": 1}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}

workout = {
    "workoutName": "30-Min Pure Recovery Flush",
    "description": "Strict Zone 1 flush. If HR goes into Zone 2, WALK. Do not fatigue the legs for Thursday's speed session.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1800,
    "estimatedDistanceInMeters": 5000,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _TIME(1800),
                    "endConditionValue": 1800,
                    "targetType": _HR_TARGET_Z1,
                    "description": "30 Min Flush (Strict Zone 1 - Cap ~145 bpm)"
                }
            ]
        }
    ]
}

tomorrow = (date.today() + timedelta(days=1)).isoformat()
try:
    res = client.upload_workout(workout)
    workout_id = res.get("workoutId")
    client.schedule_workout(workout_id, tomorrow)
    print("Scheduled Recovery Run version successfully.")
except Exception as e:
    print(f"Error: {e}")
