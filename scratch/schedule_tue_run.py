import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_DIST = lambda m: {"conditionTypeId": 3, "conditionTypeKey": "distance", "conditionValue": m, "conditionValueType": None}
_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}

_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
_HR_TARGET = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "targetValueOne": 2, "targetValueTwo": 2}

workout = {
    "workoutName": "10km Geo-Locked Track Run",
    "description": "Geographically locked: 2.7k commute to track, 4.1k track work, strides, 2.7k commute home. Total 10km.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 4200,
    "estimatedDistanceInMeters": 10000,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                    "endCondition": _DIST(2700),
                    "endConditionValue": 2700,
                    "targetType": _NO_TARGET,
                    "description": "2.7km Commute to Track (Keep HR < 130)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _DIST(4100),
                    "endConditionValue": 4100,
                    "targetType": _HR_TARGET,
                    "description": "4.1km Track Base Run (Zone 2 - Cap 174 bpm)"
                },
                {
                    "type": "RepeatGroupDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat"},
                    "numberOfIterations": 4,
                    "workoutSteps": [
                        {
                            "type": "ExecutableStepDTO",
                            "stepOrder": 1,
                            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                            "endCondition": _TIME(20),
                            "endConditionValue": 20,
                            "targetType": _NO_TARGET,
                            "description": "Stride (Accelerate to 90% speed)"
                        },
                        {
                            "type": "ExecutableStepDTO",
                            "stepOrder": 2,
                            "stepType": {"stepTypeId": 5, "stepTypeKey": "rest"},
                            "endCondition": _TIME(45),
                            "endConditionValue": 45,
                            "targetType": _NO_TARGET,
                            "description": "Walk / Slow jog recovery"
                        }
                    ]
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 4,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _DIST(2700),
                    "endConditionValue": 2700,
                    "targetType": _NO_TARGET,
                    "description": "2.7km Commute Jog Home"
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
    print("Scheduled Geo-Locked version successfully.")
except Exception as e:
    print(f"Error: {e}")
