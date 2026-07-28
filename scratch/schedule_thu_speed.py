import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

tomorrow = (date.today() + timedelta(days=1)).isoformat()

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}
_DIST = lambda m: {"conditionTypeId": 3, "conditionTypeKey": "distance", "conditionValue": m, "conditionValueType": None}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}

steps = [
    {
        "type": "ExecutableStepDTO",
        "stepOrder": 1,
        "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
        "endCondition": _LAP,
        "targetType": _NO_TARGET,
        "description": "Warmup jog (Press LAP when ready)"
    }
]

step_order = 2
for i in range(5):
    steps.append({
        "type": "ExecutableStepDTO",
        "stepOrder": step_order,
        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
        "endCondition": _DIST(1000),
        "endConditionValue": 1000,
        "targetType": _NO_TARGET,
        "description": f"Interval {i+1}/5: 1km @ Threshold (4:20-4:30/km)"
    })
    step_order += 1
    
    steps.append({
        "type": "ExecutableStepDTO",
        "stepOrder": step_order,
        "stepType": {"stepTypeId": 4, "stepTypeKey": "recovery"},
        "endCondition": _TIME(90),
        "endConditionValue": 90,
        "targetType": _NO_TARGET,
        "description": "90 seconds rest (walk/stand)"
    })
    step_order += 1

steps.append({
    "type": "ExecutableStepDTO",
    "stepOrder": step_order,
    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
    "endCondition": _LAP,
    "targetType": _NO_TARGET,
    "description": "Cooldown jog (Press LAP to finish)"
})

workout = {
    "workoutName": "5x1km Threshold (Outdoor)",
    "description": "Week 5 Day 3. 5x1km @ 4:20-4:30/km pace. 90 sec standing/walking rest. Run outdoors.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDistanceInMeters": 8000,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": steps
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
