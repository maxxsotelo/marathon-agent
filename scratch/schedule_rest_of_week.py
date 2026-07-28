import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Condition and Target Helpers
_DIST = lambda m: {"conditionTypeId": 3, "conditionTypeKey": "distance", "conditionValue": m, "conditionValueType": None}
_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}
_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}

_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
_HR_TARGET_Z2 = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "targetValueOne": 2, "targetValueTwo": 2}
_HR_TARGET_Z4 = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "targetValueOne": 4, "targetValueTwo": 4}


# --- THURSDAY: 6x800m ---
workout_thu = {
    "workoutName": "6x800m VO2 Max Intervals",
    "description": "Geo-locked. 2.7k commute, 6x800m @ 4:00/km w/ 400m recovery, 2.7k commute home.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 4500,
    "estimatedDistanceInMeters": 12600,
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
                    "type": "RepeatGroupDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat"},
                    "numberOfIterations": 6,
                    "workoutSteps": [
                        {
                            "type": "ExecutableStepDTO",
                            "stepOrder": 1,
                            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                            "endCondition": _DIST(800),
                            "endConditionValue": 800,
                            "targetType": _NO_TARGET, # Letting user run by feel/pace
                            "description": "800m Sprint (Target 4:00/km or faster)"
                        },
                        {
                            "type": "ExecutableStepDTO",
                            "stepOrder": 2,
                            "stepType": {"stepTypeId": 5, "stepTypeKey": "rest"},
                            "endCondition": _DIST(400),
                            "endConditionValue": 400,
                            "targetType": _NO_TARGET,
                            "description": "400m Slow Recovery Jog"
                        }
                    ]
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
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

# --- SUNDAY: 21km LONG RUN ---
workout_sun = {
    "workoutName": "21.1km The Long Run",
    "description": "Half-Marathon base run on pre-fatigued legs.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 8400,
    "estimatedDistanceInMeters": 21100,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                    "endCondition": _TIME(600),
                    "endConditionValue": 600,
                    "targetType": _NO_TARGET,
                    "description": "10 min Warmup (Keep HR under 130 bpm)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _DIST(21100),
                    "endConditionValue": 21100,
                    "targetType": _HR_TARGET_Z2,
                    "description": "21.1 km Base Run (Zone 2 - Cap 174 bpm)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Cooldown Jog home (Press lap to end)"
                }
            ]
        }
    ]
}

dates = {
    "2026-07-16": workout_thu,
    "2026-07-19": workout_sun
}

for d, w in dates.items():
    try:
        res = client.upload_workout(w)
        workout_id = res.get("workoutId")
        client.schedule_workout(workout_id, d)
        print(f"Scheduled {w['workoutName']} for {d}")
    except Exception as e:
        print(f"Error scheduling {w['workoutName']}: {e}")
