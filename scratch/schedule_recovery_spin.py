import os, datetime
from garminconnect import Garmin
from dotenv import load_dotenv

load_dotenv()
email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

client = Garmin(email, password)
client.login()

workout_name = "Active Recovery Spin"
workout_desc = "30-40 minute light spin. Strictly Zone 1. Keep HR below 120 bpm. High cadence, low resistance."
sport = "CYCLING"

workout_payload = {
    "workoutName": workout_name,
    "description": workout_desc,
    "sportType": {
        "sportTypeId": 2,
        "sportTypeKey": "cycling"
    },
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {
                "sportTypeId": 2,
                "sportTypeKey": "cycling"
            },
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepId": None,
                    "stepOrder": 1,
                    "childStepId": None,
                    "description": "Light Spin",
                    "stepType": {
                        "stepTypeId": 3,
                        "stepTypeKey": "recovery"
                    },
                    "endCondition": {
                        "conditionTypeKey": "time",
                        "conditionTypeId": 2
                    },
                    "endConditionValue": 40 * 60,
                    "targetType": {
                        "workoutTargetTypeId": 4,
                        "workoutTargetTypeKey": "heart.rate.zone"
                    },
                    "targetValueOne": 1,
                    "targetValueTwo": 1
                }
            ]
        }
    ]
}

print("Saving workout...")
response = client.save_workout(workout_payload)
workout_id = response.get("workoutId")
print(f"Workout saved. ID: {workout_id}")

print("Scheduling for today...")
client.schedule_workout(workout_id, "2026-05-26")
print("Successfully scheduled.")
