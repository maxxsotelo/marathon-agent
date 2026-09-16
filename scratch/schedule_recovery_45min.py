"""
schedule_recovery_45min.py
Schedules a 45-minute time-based recovery run to Garmin Connect for today.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

workout_name = "Recovery Flush (Time-Based)"
workout_notes = "Engine Note: User override accepted. Mechanical ACWR clears this load (0.947). Keep HR strictly in Zone 1 / low Zone 2 to preserve glycogen for Thursday's VO2 Max."

workout_payload = {
    "workoutName": workout_name,
    "description": workout_notes,
    "sport": "RUNNING",
    "subSport": "STREET",
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sport": "RUNNING",
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "active"},
                    "endCondition": {"conditionTypeId": 2, "conditionTypeKey": "time"},
                    "endConditionValue": 45 * 60, # 45 mins in seconds
                    "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
                    "targetValueOne": 1,
                    "targetValueTwo": 2, # HR Zones 1-2
                    "stepId": None
                }
            ]
        }
    ]
}

try:
    print(f"Creating workout: {workout_name}...")
    workout = client.add_workout(workout_payload)
    workout_id = workout['workoutId']
    print(f"Workout created with ID: {workout_id}")
    
    today = date(2026, 7, 28).isoformat()
    client.schedule_workout(workout_id, today)
    print(f"Workout successfully scheduled for {today}")
except Exception as e:
    print(f"Failed to schedule workout: {e}")
