"""
Workout Generator Module for Antigravity Marathon Agent
========================================================
Creates structured Garmin-compatible workouts and schedules them
to the athlete's Garmin Connect calendar.

Athlete Profile (from operating_manual.md — LTHR Method, Updated June 6 2026):
    - Max HR: 206 bpm
    - LTHR: ~191 bpm | RHR: 39 bpm
    - Zone 1 (Easy Aerobic):   < 162 bpm      (< 85% LTHR) — all easy/long runs
    - Zone 2 (Extensive):      162 – 174 bpm  (85–91% LTHR)
    - Zone 3 (Tempo):          174 – 181 bpm  (91–95% LTHR)
    - Zone 4 (Threshold):      181 – 191 bpm  (95–100% LTHR)
    - Zone 5 (VO2 Max):        > 191 bpm      (> 100% LTHR)
    - MAF Cross-check ceiling: 155 bpm (conservative floor for pure aerobic)
    - Easy Cadence:            Self-select (~163–170 spm at easy pace)
    - Speed Cadence:           175–182+ spm at tempo/threshold
    - Easy/Long Pace:          6:00-6:45 /km
    - Threshold Pace:          4:35-4:45 /km (heat adjusted)
    - 5K Pace:                 ~4:49 /km
"""

import os
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin
from garminconnect.workout import (
    RunningWorkout,
    CyclingWorkout,
    WorkoutSegment,
    ExecutableStep,
    RepeatGroup,
    create_warmup_step,
    create_interval_step,
    create_recovery_step,
    create_cooldown_step,
    create_repeat_group,
    SportType,
    StepType,
    ConditionType,
    TargetType,
)

load_dotenv()
email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

TOKEN_STORE = os.path.expanduser("~/.garminconnect")

# ──────────────────────────────────────────────────────────────────────
# ATHLETE HEART RATE ZONES (LTHR Method — Updated June 6 2026)
# Source: operating_manual.md Section 1 — LTHR ~191 bpm, RHR 39 bpm
# IMPORTANT: Zone naming follows LTHR convention, NOT Garmin's 5-zone model.
# Zone 1 = Easy Aerobic (<162 bpm). Zone 2 = Extensive (162-174 bpm).
# ──────────────────────────────────────────────────────────────────────
HR_ZONES = {
    1: {"name": "Easy Aerobic",  "low": 130, "high": 161},  # <162 bpm — all easy/long runs
    2: {"name": "Extensive",     "low": 162, "high": 174},  # 85-91% LTHR
    3: {"name": "Tempo",         "low": 174, "high": 181},  # 91-95% LTHR
    4: {"name": "Threshold",     "low": 181, "high": 191},  # 95-100% LTHR
    5: {"name": "VO2 Max",       "low": 191, "high": 206},  # >100% LTHR
}

MAX_HR   = 206
ZONE1_CAP = 162  # Hard cap for all easy/long runs
ZONE2_CAP = 174  # New Zone 2 ceiling (LTHR method, June 6 2026)

# ──────────────────────────────────────────────────────────────────────
# PACE BENCHMARKS (operating_manual.md, heat-adjusted for Marikina)
# Garmin target speed is in meters/second.
# ──────────────────────────────────────────────────────────────────────
def pace_to_mps(min_per_km: str) -> float:
    """Convert a pace string like '6:00' (min/km) to meters per second."""
    parts = min_per_km.split(":")
    total_seconds = int(parts[0]) * 60 + int(parts[1])
    return 1000.0 / total_seconds

PACE_BENCHMARKS = {
    "recovery":   {"low": pace_to_mps("7:30"), "high": pace_to_mps("6:45")},
    "easy":       {"low": pace_to_mps("6:45"), "high": pace_to_mps("6:00")},
    "marathon":   {"low": pace_to_mps("5:50"), "high": pace_to_mps("5:30")},
    "threshold":  {"low": pace_to_mps("4:55"), "high": pace_to_mps("4:35")},
    "vo2max":     {"low": pace_to_mps("4:50"), "high": pace_to_mps("4:30")},
}


# ──────────────────────────────────────────────────────────────────────
# HELPER: Build target dicts + extra kwargs for workout steps
# ──────────────────────────────────────────────────────────────────────
# Garmin API NOTE:
#   The `targetType` dict on ExecutableStep only identifies the TARGET
#   KIND (HR, pace, no-target). The actual VALUES (targetValueOne,
#   targetValueTwo, zoneNumber) must be set as *sibling* fields on the
#   ExecutableStep itself — NOT nested inside targetType.
#
#   ExecutableStep uses Pydantic's `extra="allow"`, so we can pass any
#   extra kwargs when constructing the step and they will serialize.
# ──────────────────────────────────────────────────────────────────────

def _hr_target_type() -> dict:
    """Return the targetType identifier dict for custom absolute BPM targets.
    Using 'heart.rate' (not 'heart.rate.zone') so Garmin reads our exact
    BPM values rather than its own miscalibrated zone table.
    """
    return {
        "workoutTargetTypeId": TargetType.HEART_RATE,
        "workoutTargetTypeKey": "heart.rate",
        "displayOrder": 3,
    }


def _hr_target_values(zone: int) -> dict:
    """
    Return the extra kwargs (targetValueOne, targetValueTwo) that must be
    set directly on ExecutableStep for custom absolute BPM targets.
    No zoneNumber — we bypass Garmin's zone table entirely.
    """
    z = HR_ZONES[zone]
    return {
        "targetValueOne": float(z["low"]),
        "targetValueTwo": float(z["high"]),
    }


def _pace_target_type() -> dict:
    """Return the targetType identifier dict for speed/pace targets."""
    return {
        "workoutTargetTypeId": TargetType.SPEED,
        "workoutTargetTypeKey": "speed.zone",
        "displayOrder": 5,
    }


def _pace_target_values(intensity: str) -> dict:
    """
    Return the extra kwargs (targetValueOne, targetValueTwo) that must
    be set directly on ExecutableStep for pace/speed targets.
    """
    p = PACE_BENCHMARKS[intensity]
    return {
        "targetValueOne": p["low"],
        "targetValueTwo": p["high"],
    }


def _no_target_type() -> dict:
    """Return the targetType dict for steps with no target."""
    return {
        "workoutTargetTypeId": TargetType.NO_TARGET,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1,
    }


# ──────────────────────────────────────────────────────────────────────
# HELPER: Build a complete step with HR and/or pace targets
# ──────────────────────────────────────────────────────────────────────
# Pydantic V2 with extra="allow" requires extra fields to be passed
# at construction time — object.__setattr__ does NOT register them
# in the model's serialization. We construct ExecutableStep directly.
# ──────────────────────────────────────────────────────────────────────

# Step type descriptors (matching the library's convention)
_STEP_TYPES = {
    "warmup":   {"stepTypeId": StepType.WARMUP,   "stepTypeKey": "warmup",   "displayOrder": 1},
    "interval": {"stepTypeId": StepType.INTERVAL,  "stepTypeKey": "interval", "displayOrder": 3},
    "recovery": {"stepTypeId": StepType.RECOVERY,  "stepTypeKey": "recovery", "displayOrder": 4},
    "cooldown": {"stepTypeId": StepType.COOLDOWN,  "stepTypeKey": "cooldown", "displayOrder": 2},
}

_TIME_CONDITION = {
    "conditionTypeId": ConditionType.TIME,
    "conditionTypeKey": "time",
    "displayOrder": 2,
    "displayable": True,
}


def _build_step(step_key: str, duration_secs: float, step_order: int,
                zone: int, pace_intensity: str | None = None) -> ExecutableStep:
    """
    Construct an ExecutableStep with HR zone values and optional pace
    as top-level fields (the way Garmin's API actually expects them).
    """
    hr_vals = _hr_target_values(zone)

    # Build the constructor kwargs
    kwargs = {
        "stepOrder": step_order,
        "stepType": _STEP_TYPES[step_key],
        "endCondition": _TIME_CONDITION,
        "endConditionValue": duration_secs,
        "targetType": _hr_target_type(),
        "targetValueOne": hr_vals["targetValueOne"],
        "targetValueTwo": hr_vals["targetValueTwo"],
    }

    # Add pace as secondary target if specified
    if pace_intensity:
        pv = _pace_target_values(pace_intensity)
        kwargs["secondaryTargetType"] = _pace_target_type()
        kwargs["secondaryTargetValueOne"] = pv["targetValueOne"]
        kwargs["secondaryTargetValueTwo"] = pv["targetValueTwo"]

    return ExecutableStep(**kwargs)


def _make_warmup(duration_secs: float, step_order: int, zone: int,
                 pace_intensity: str | None = None) -> ExecutableStep:
    """Create a warmup step with HR zone target and optional pace."""
    return _build_step("warmup", duration_secs, step_order, zone, pace_intensity)


def _make_interval(duration_secs: float, step_order: int, zone: int,
                   pace_intensity: str | None = None) -> ExecutableStep:
    """Create an interval step with HR zone target and optional pace."""
    return _build_step("interval", duration_secs, step_order, zone, pace_intensity)


def _make_recovery(duration_secs: float, step_order: int, zone: int = 1,
                   pace_intensity: str | None = None) -> ExecutableStep:
    """Create a recovery step with HR zone target."""
    return _build_step("recovery", duration_secs, step_order, zone, pace_intensity)


def _make_cooldown(duration_secs: float, step_order: int, zone: int = 1,
                   pace_intensity: str | None = None) -> ExecutableStep:
    """Create a cooldown step with HR zone target."""
    return _build_step("cooldown", duration_secs, step_order, zone, pace_intensity)


# ──────────────────────────────────────────────────────────────────────
# CORE: create_workout()
# ──────────────────────────────────────────────────────────────────────
def create_workout(
    workout_type: str,
    duration_mins: int,
    intensity: str = "easy",
    sport: str = "run",
):
    """
    Create a Garmin-compatible structured running workout.

    Parameters
    ----------
    workout_type : str
        One of: 'easy', 'long_run', 'tempo', 'intervals', 'recovery'
    duration_mins : int
        Total estimated workout duration in minutes.
    intensity : str
        Target intensity key: 'recovery', 'easy', 'marathon',
        'threshold', 'vo2max'. Maps to the athlete's verified
        HR zones and pace benchmarks.

    Returns
    -------
    RunningWorkout
        A Pydantic model ready for upload via
        client.upload_running_workout(workout).
    """
    workout_type = workout_type.lower().strip()
    intensity = intensity.lower().strip()
    total_secs = duration_mins * 60

    # Map intensity string to the closest HR zone number.
    # NOTE: For this athlete, 'vo2max' maps to Zone 4 (185-196 bpm),
    # NOT Zone 5. His verified LTHR is 190-196 bpm, meaning Zone 4 IS
    # the VO2 Max stimulus. Zone 5 (197+ bpm) is pure anaerobic sprint
    # territory — only appropriate for <30 second efforts.
    intensity_to_zone = {
        "recovery":  1,
        "easy":      2,
        "marathon":  3,
        "threshold": 4,
        "vo2max":    4,  # LTHR-anchored: 185-196 bpm = VO2 Max for Max
    }
    zone = intensity_to_zone.get(intensity, 2)

    # ── Build steps based on workout type ──────────────────────────
    if workout_type == "recovery":
        steps = _build_recovery_steps(total_secs)
        name = f"Recovery Run – Zone 1 ({duration_mins}min)"

    elif workout_type == "easy":
        steps = _build_easy_steps(total_secs, zone)
        name = f"Easy Run – Zone {zone} ({duration_mins}min)"

    elif workout_type == "long_run":
        steps = _build_long_run_steps(total_secs)
        name = f"Long Run – Aerobic Base ({duration_mins}min)"

    elif workout_type == "tempo":
        steps = _build_tempo_steps(total_secs, zone)
        name = f"Tempo Run – Zone {zone} ({duration_mins}min)"

    elif workout_type == "intervals":
        steps = _build_interval_steps(total_secs, zone, intensity)
        name = f"Interval Session – Zone {zone} ({duration_mins}min)"

    else:
        raise ValueError(
            f"Unknown workout_type '{workout_type}'. "
            f"Choose from: easy, long_run, tempo, intervals, recovery"
        )

    if sport == "bike":
        workout = CyclingWorkout(
            workoutName=name,
            description=f"Auto-generated by Antigravity Coach for Max. "
                        f"Intensity: {intensity} | Custom HR: {HR_ZONES[zone]['low']}-{HR_ZONES[zone]['high']} bpm (physiology-calibrated)",
            estimatedDurationInSecs=total_secs,
            workoutSegments=[
                WorkoutSegment(
                    segmentOrder=1,
                    sportType={
                        "sportTypeId": SportType.CYCLING,
                        "sportTypeKey": "cycling",
                    },
                    workoutSteps=steps,
                )
            ],
        )
    else:
        workout = RunningWorkout(
            workoutName=name,
            description=f"Auto-generated by Antigravity Coach for Max. "
                        f"Intensity: {intensity} | Custom HR: {HR_ZONES[zone]['low']}-{HR_ZONES[zone]['high']} bpm (physiology-calibrated)",
            estimatedDurationInSecs=total_secs,
            workoutSegments=[
                WorkoutSegment(
                    segmentOrder=1,
                    sportType={
                        "sportTypeId": SportType.RUNNING,
                        "sportTypeKey": "running",
                    },
                    workoutSteps=steps,
                )
            ],
        )

    print(f"[WORKOUT] Created: {name}")
    print(f"[WORKOUT] Target HR Zone {zone}: "
          f"{HR_ZONES[zone]['low']}-{HR_ZONES[zone]['high']} bpm")
    return workout


# ──────────────────────────────────────────────────────────────────────
# STEP BUILDERS (each returns a list of ExecutableStep / RepeatGroup)
# All steps now use _make_*() helpers that correctly set HR zone values
# and optional pace targets as top-level fields on ExecutableStep.
# ──────────────────────────────────────────────────────────────────────

# Map intensity string → pace benchmark key for secondary pace targets
INTENSITY_TO_PACE = {
    "recovery":  "recovery",
    "easy":      "easy",
    "marathon":  "marathon",
    "threshold": "threshold",
    "vo2max":    "vo2max",
}


def _build_recovery_steps(total_secs: int) -> list:
    """Zone 1 only. No structure needed — just easy movement."""
    warmup_secs = 300.0  # 5 min
    cooldown_secs = 300.0  # 5 min
    main_secs = float(total_secs) - warmup_secs - cooldown_secs
    if main_secs < 300:
        main_secs = float(total_secs)
        return [
            _make_warmup(main_secs, step_order=1, zone=1,
                         pace_intensity="recovery"),
        ]
    return [
        _make_warmup(warmup_secs, step_order=1, zone=1,
                     pace_intensity="recovery"),
        _make_interval(main_secs, step_order=2, zone=1,
                       pace_intensity="recovery"),
        _make_cooldown(cooldown_secs, step_order=3, zone=1,
                       pace_intensity="recovery"),
    ]


def _build_easy_steps(total_secs: int, zone: int) -> list:
    """Aerobic base: warm up → steady Zone 2 → cool down."""
    warmup_secs = 600.0  # 10 min
    cooldown_secs = 300.0  # 5 min
    main_secs = float(total_secs) - warmup_secs - cooldown_secs
    if main_secs < 600:
        # Short run — skip formal warm/cool
        return [
            _make_warmup(float(total_secs), step_order=1, zone=zone,
                         pace_intensity="easy"),
        ]
    return [
        _make_warmup(warmup_secs, step_order=1, zone=1,
                     pace_intensity="recovery"),
        _make_interval(main_secs, step_order=2, zone=zone,
                       pace_intensity="easy"),
        _make_cooldown(cooldown_secs, step_order=3, zone=1,
                       pace_intensity="recovery"),
    ]


def _build_long_run_steps(total_secs: int) -> list:
    """
    Long run protocol from operating_manual.md:
    First ~70% at Zone 2 easy, final ~30% at Marathon Pace (Zone 3).
    Always includes warm-up and cool-down.
    """
    warmup_secs = 600.0  # 10 min
    cooldown_secs = 600.0  # 10 min
    body_secs = float(total_secs) - warmup_secs - cooldown_secs
    return [
        _make_warmup(warmup_secs, step_order=1, zone=1,
                     pace_intensity="recovery"),
        # Main aerobic block — respect the requested intensity zone
        _make_interval(body_secs, step_order=2, zone=2,
                       pace_intensity="easy"),
        _make_cooldown(cooldown_secs, step_order=3, zone=1,
                       pace_intensity="recovery"),
    ]


def _build_tempo_steps(total_secs: int, zone: int) -> list:
    """
    Continuous tempo run at the specified zone.
    Warm-up 10 min → Sustained effort → Cool-down 10 min.
    """
    warmup_secs = 600.0
    cooldown_secs = 600.0
    tempo_secs = float(total_secs) - warmup_secs - cooldown_secs
    if tempo_secs < 600:
        tempo_secs = 600.0  # minimum 10-min tempo block

    # Map zone to the matching pace intensity
    pace_key = {3: "marathon", 4: "threshold"}.get(zone, "easy")

    return [
        _make_warmup(warmup_secs, step_order=1, zone=1,
                     pace_intensity="recovery"),
        _make_interval(tempo_secs, step_order=2, zone=zone,
                       pace_intensity=pace_key),
        _make_cooldown(cooldown_secs, step_order=3, zone=1,
                       pace_intensity="recovery"),
    ]


def _build_interval_steps(total_secs: int, zone: int, intensity: str) -> list:
    """
    Structured interval session.

    FT-dominant athlete protocol (from training_fast_vs_slow_twitch):
    - Short work bouts (2 min) with long passive recovery (3 min)
    - For VO2 Max: 600m reps (~2:40 at 4:30/km pace)

    Builds a warm-up → repeat(work + rest) → cool-down structure.
    """
    warmup_secs = 600.0   # 10 min
    cooldown_secs = 600.0  # 10 min

    # Work and rest durations based on intensity
    if intensity == "vo2max":
        work_secs = 160.0   # ~2:40 (600m at ~4:30/km)
        rest_secs = 180.0   # 3:00 passive recovery
    elif intensity == "threshold":
        work_secs = 300.0   # 5:00 threshold reps
        rest_secs = 120.0   # 2:00 recovery jog
    else:
        work_secs = 240.0   # 4:00 moderate reps
        rest_secs = 120.0   # 2:00 recovery

    available_secs = float(total_secs) - warmup_secs - cooldown_secs
    reps = max(1, int(available_secs / (work_secs + rest_secs)))

    # Build the work + rest steps inside the repeat group
    # Pace target for work bouts matches the intensity
    pace_key = INTENSITY_TO_PACE.get(intensity, "easy")
    work_step = _make_interval(work_secs, step_order=1, zone=zone,
                               pace_intensity=pace_key)
    rest_step = _make_recovery(rest_secs, step_order=2, zone=1,
                               pace_intensity="recovery")

    repeat = create_repeat_group(
        iterations=reps,
        workout_steps=[work_step, rest_step],
        step_order=2,
    )

    return [
        _make_warmup(warmup_secs, step_order=1, zone=1,
                     pace_intensity="recovery"),
        repeat,
        _make_cooldown(cooldown_secs, step_order=3, zone=1,
                       pace_intensity="recovery"),
    ]


# ──────────────────────────────────────────────────────────────────────
# ACWR SAFETY SYSTEM
# ──────────────────────────────────────────────────────────────────────

class SpeedVetoError(Exception):
    pass

def calculate_current_acwr(client: Garmin) -> float:
    """Calculate ACWR using the last 28 days of activities (running)."""
    from datetime import date, timedelta
    today = date.today()
    start_date = today - timedelta(days=28)
    
    # Fetch all activities in the last 28 days to prevent undercounting
    activities = client.get_activities_by_date(start_date.isoformat(), today.isoformat())
    
    acute_km = 0.0
    chronic_km = 0.0
    
    run_types = ("running", "treadmill_running", "trail_running", "indoor_running")
    for a in activities:
        atype = a.get("activityType", {}).get("typeKey")
        if atype not in run_types:
            continue
            
        start_str = a.get("startTimeLocal", "2000-01-01")[:10]
        try:
            act_date = date.fromisoformat(start_str)
        except ValueError:
            continue
            
        days_ago = (today - act_date).days
        if days_ago < 0 or days_ago > 28:
            continue
            
        dist_km = (a.get("distance") or 0) / 1000.0
        if days_ago <= 7:
            acute_km += dist_km
        chronic_km += dist_km
            
    chronic_avg = chronic_km / 4.0
    return acute_km / chronic_avg if chronic_avg > 0 else 0.0

def enforce_acwr_safety(client: Garmin, workout):
    """Enforce the Speed Veto if ACWR is > 1.5 and the workout contains high intensity."""
    if not isinstance(workout, RunningWorkout):
        return  # We don't block cycling or other cross-training
        
    has_speed = False
    name = getattr(workout, "workoutName", "").lower()
    desc = (getattr(workout, "description", "") or "").lower()
    
    speed_keywords = ["threshold", "tempo", "vo2", "vo2max", "interval", "fartlek", "speed"]
    if any(k in name or k in desc for k in speed_keywords):
        has_speed = True
        
    if has_speed:
        acwr = calculate_current_acwr(client)
        if acwr > 1.5:
            raise SpeedVetoError(
                f"SPEED VETO ENGAGED: Your ACWR is {acwr:.3f}. "
                "You cannot schedule speedwork or threshold runs while in the Danger Zone."
            )

# ──────────────────────────────────────────────────────────────────────
# UPLOAD & SCHEDULE
# ──────────────────────────────────────────────────────────────────────

def _get_client() -> Garmin:
    """Authenticate and return a Garmin client using saved tokens."""
    client = Garmin(
        email=email,
        password=password,
        prompt_mfa=lambda: input("Garmin MFA code: "),
    )
    client.login(TOKEN_STORE)
    return client


def upload_workout(workout) -> dict:
    """
    Upload a workout to Garmin Connect.

    Returns the API response dict which includes 'workoutId'.
    """
    client = _get_client()
    
    # [KIAT ENGINE] Enforce physiological constraints before upload
    enforce_acwr_safety(client, workout)
    
    if isinstance(workout, CyclingWorkout):
        result = client.upload_cycling_workout(workout)
    else:
        result = client.upload_running_workout(workout)
    workout_id = result.get("workoutId", "unknown")
    print(f"[UPLOAD] Workout uploaded successfully. ID: {workout_id}")
    return result


def schedule_workout(workout_id: int, target_date: str) -> dict:
    """
    Schedule an existing workout to a specific date on the
    athlete's Garmin Connect calendar.

    Parameters
    ----------
    workout_id : int
        The workout ID returned from upload_workout().
    target_date : str
        Date string in 'YYYY-MM-DD' format.

    Returns
    -------
    dict
        API response from Garmin Connect.
    """
    client = _get_client()
    result = client.schedule_workout(workout_id, target_date)
    print(f"[SCHEDULE] Workout {workout_id} scheduled for {target_date}")
    return result


def create_and_schedule(
    workout_type: str,
    duration_mins: int,
    intensity: str,
    target_date: str,
) -> dict:
    """
    End-to-end convenience: create → upload → schedule.

    Parameters
    ----------
    workout_type : str
        One of: 'easy', 'long_run', 'tempo', 'intervals', 'recovery'
    duration_mins : int
        Total estimated workout duration in minutes.
    intensity : str
        Target intensity: 'recovery', 'easy', 'marathon',
        'threshold', 'vo2max'.
    target_date : str
        Date string in 'YYYY-MM-DD' format.

    Returns
    -------
    dict
        Contains 'workout' (the RunningWorkout object),
        'upload_result', and 'schedule_result'.
    """
    workout = create_workout(workout_type, duration_mins, intensity)
    upload_result = upload_workout(workout)
    workout_id = upload_result.get("workoutId")
    schedule_result = schedule_workout(workout_id, target_date)
    return {
        "workout": workout,
        "upload_result": upload_result,
        "schedule_result": schedule_result,
    }


# ──────────────────────────────────────────────────────────────────────
# CLI INTERFACE
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse, subprocess, sys

    parser = argparse.ArgumentParser(
        description="Antigravity Workout Generator -- Create & schedule "
                    "Garmin workouts from the command line."
    )
    parser.add_argument(
        "type",
        choices=["easy", "long_run", "tempo", "intervals", "recovery"],
        help="Workout type",
    )
    parser.add_argument(
        "duration",
        type=int,
        help="Duration in minutes",
    )
    parser.add_argument(
        "--intensity",
        default="easy",
        choices=["recovery", "easy", "marathon", "threshold", "vo2max"],
        help="Target intensity (default: easy)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Schedule date (YYYY-MM-DD). If omitted, creates without scheduling.",
    )
    parser.add_argument(
        "--sport",
        choices=["run", "bike"],
        default="run",
        help="Sport type for the workout (default: run)"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload the workout to Garmin Connect.",
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="[EMERGENCY ONLY] Skip pre_schedule_check.py gate. "
             "This must never be used routinely. Every use is a protocol violation."
    )

    args = parser.parse_args()

    # ── MANDATORY PRE-SCHEDULE GATE (RULE 00) ──────────────────────────────
    # This block runs pre_schedule_check.py before EVERY --upload.
    # It cannot be removed. --skip-check exists for true emergencies only
    # and prints a loud warning when used.
    if args.upload:
        if args.skip_check:
            print("[!!!!] --skip-check flag used. PROTOCOL VIOLATION.")
            print("       This bypasses pre_schedule_check.py. Every use must be")
            print("       explicitly justified in the session log. Do not use routinely.")
        else:
            print("[GATE] Running mandatory pre_schedule_check.py...")
            check_script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "pre_schedule_check.py"
            )
            result = subprocess.run(
                [sys.executable, check_script,
                 "--type",      args.type,
                 "--duration",  str(args.duration),
                 "--intensity", args.intensity],
                capture_output=False  # let it print directly to terminal
            )
            if result.returncode != 0:
                print("[GATE] Pre-schedule check BLOCKED the upload. Exiting.")
                print("       Resolve the issue flagged above before scheduling.")
                sys.exit(1)
            print("[GATE] Pre-schedule check CLEARED. Proceeding with upload.\n")
    # ── END GATE ────────────────────────────────────────────────────────────

    workout = create_workout(args.type, args.duration, args.intensity, args.sport)

    if args.upload:
        result = upload_workout(workout)
        wid = result.get("workoutId")

        if args.date and wid:
            schedule_workout(wid, args.date)
    elif args.date:
        print("[INFO] Use --upload together with --date to schedule.")

    print("\n[DONE] Workout object ready.")
    print(f"  Name:     {workout.workoutName}")
    print(f"  Duration: {args.duration} min")
    print(f"  Steps:    {len(workout.workoutSegments[0].workoutSteps)}")

