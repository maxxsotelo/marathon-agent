import os
import sys
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin
from garminconnect.workout import (
    RunningWorkout,
    WorkoutSegment,
    ExecutableStep,
    SportType,
    StepType,
    ConditionType,
    TargetType,
)

load_dotenv()
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA: "),
)
client.login(TOKEN_STORE)

today = date.today()
today_str = today.strftime("%Y-%m-%d")

print(f"Scheduling Track Tempo Workout for {today_str}...")

# Athlete Heart Rate Zones (LTHR Method)
# Zone 1 (Easy Aerobic): < 162 bpm (130-161 bpm)
# Zone 3 (Tempo / Marathon Pace): 175-181 bpm
HR_ZONES = {
    1: {"low": 130, "high": 161},
    2: {"low": 162, "high": 174},
    3: {"low": 175, "high": 181},
    4: {"low": 182, "high": 191},
    5: {"low": 192, "high": 206},
}

_HR_TARGET_TYPE = {
    "workoutTargetTypeId": TargetType.HEART_RATE,
    "workoutTargetTypeKey": "heart.rate.zone",
    "displayOrder": 1,
}

_DISTANCE_CONDITION = {
    "conditionTypeId": 3,
    "conditionTypeKey": "distance",
    "displayOrder": 3,
    "displayable": True,
}

_STEP_TYPES = {
    "warmup":   {"stepTypeId": StepType.WARMUP,   "stepTypeKey": "warmup",   "displayOrder": 1},
    "interval": {"stepTypeId": StepType.INTERVAL,  "stepTypeKey": "interval", "displayOrder": 3},
    "cooldown": {"stepTypeId": StepType.COOLDOWN,  "stepTypeKey": "cooldown", "displayOrder": 2},
}

# 1. Warm-up to track: 2.7 km (2700m) in Zone 1 (130-161 bpm)
step1 = ExecutableStep(
    stepOrder=1,
    stepType=_STEP_TYPES["warmup"],
    endCondition=_DISTANCE_CONDITION,
    endConditionValue=2700.0,
    targetType=_HR_TARGET_TYPE,
    targetValueOne=float(HR_ZONES[1]["low"]),
    targetValueTwo=float(HR_ZONES[1]["high"]),
    description="Run to the track in easy Zone 1 (< 161 bpm)"
)

# 2. Track Tempo Block: 4.0 km (4000m / 10 laps) in Zone 3 (175-181 bpm)
step2 = ExecutableStep(
    stepOrder=2,
    stepType=_STEP_TYPES["interval"],
    endCondition=_DISTANCE_CONDITION,
    endConditionValue=4000.0,
    targetType=_HR_TARGET_TYPE,
    targetValueOne=float(HR_ZONES[3]["low"]),
    targetValueTwo=float(HR_ZONES[3]["high"]),
    description="Track Tempo Block: 10 laps @ Marathon Pace (175-181 bpm)"
)

# 3. Cool-down home: 2.7 km (2700m) in Zone 1 (130-161 bpm)
step3 = ExecutableStep(
    stepOrder=3,
    stepType=_STEP_TYPES["cooldown"],
    endCondition=_DISTANCE_CONDITION,
    endConditionValue=2700.0,
    targetType=_HR_TARGET_TYPE,
    targetValueOne=float(HR_ZONES[1]["low"]),
    targetValueTwo=float(HR_ZONES[1]["high"]),
    description="Cool-down jog/walk back home in Zone 1"
)

workout_name = "Track Tempo – 4km MP (9.4km Total)"
workout = RunningWorkout(
    workoutName=workout_name,
    description="2.7km Warmup to track in Zone 1 (<161 bpm) + 4.0km Track Tempo in Zone 3 (175-181 bpm) + 2.7km Cooldown home in Zone 1",
    estimatedDurationInSecs=3300,
    workoutSegments=[
        WorkoutSegment(
            segmentOrder=1,
            sportType={
                "sportTypeId": SportType.RUNNING,
                "sportTypeKey": "running",
            },
            workoutSteps=[step1, step2, step3],
        )
    ],
)

res = client.upload_running_workout(workout)
workout_id = res.get("workoutId")
print(f"[UPLOAD] Workout uploaded successfully! ID: {workout_id}")

client.schedule_workout(workout_id, today_str)
print(f"[SCHEDULE] Workout {workout_id} successfully scheduled for {today_str}!")
