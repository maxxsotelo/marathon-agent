# AGENT SCHEDULING PROTOCOL
# =============================================================================
# MANDATORY READING FOR ALL LLM INSTANCES
# This protocol governs ALL workout scheduling actions in this repository.
# Under no circumstances should any LLM deviate from these patterns or
# attempt to improvise a new scheduling method.
# =============================================================================

## RULE 00: Mandatory Pre-Schedule Justification Gate (NO EXCEPTIONS)

### Step 1 — Load the Weekly Plan
Before giving ANY daily training advice or answering "what should I do today":

```bash
python current_week_plan.py
```

`marathon-agent/current_week_plan.py` is the SINGLE SOURCE OF TRUTH for the
active training week. Updated every Sunday. Never use conversation memory instead.

### Step 2 — Run the Pre-Schedule Check before EVERY upload
Before calling `workout_generator.py --upload` for ANY workout, the agent MUST
first run:

```bash
python pre_schedule_check.py --type <type> --duration <minutes> --intensity <intensity>
```

This script:
- Loads today's session from `current_week_plan.py`
- Computes verified ACWR from live Garmin data (not check_vitals.py which has a known bug)
- Prints the last 8 weeks of mileage history to justify the load target
- Prints current LTHR HR zones so the agent doesn't use stale zone data
- Blocks scheduling (exit code 1) if ACWR > 1.5 and a quality session is requested
- Prints a final CLEARED / BLOCKED verdict

If `pre_schedule_check.py` exits with code 1, do NOT proceed. Respect the veto.
If it exits with code 0, proceed with `workout_generator.py --upload`.

Violating this rule causes the agent to schedule wrong sessions, wrong HR zones,
wrong exercise choices, and unsupported weekly volume — as occurred on 2026-06-18.

---

## RULE 01: Deep Run Audit — MANDATORY After Every Run (NO EXCEPTIONS)

Whenever the user returns after a run (any phrase like "I just got back", "I finished my run",
"just got home", "give me my run analysis"), the agent MUST immediately run:

```bash
python "C:\Users\Max\.gemini\antigravity\brain\3a089547-6db7-486f-9c49-05bc442734f2\scratch\deep_run_audit.py"
```

This script pulls ALL of the following from Garmin automatically:
- Full activity summary (distance, pace, GAP, HR, cadence, power, stride, GCT, vert osc)
- Lap-by-lap breakdown with HR zones labeled per the CURRENT LTHR method
- Environment data (temp) + Heat Index via Rothfusz regression
- Terrain summary (elevation gain/loss, terrain score, rolling vs flat classification)
- HR zone distribution (time in each zone as percentage)
- TRIMP (Banister training load score)

The agent MUST NOT give a run analysis based on only a summary-level API call.
The agent MUST NOT guess or paraphrase telemetry. Only data from the script is authoritative.

If today's run is not yet synced, wait and retry with `--id <activityId>` once the user
confirms the activity is visible on Garmin Connect.

### Why this rule exists
On 2026-06-18, the agent gave a shallow analysis (distance, pace, avg HR only) when the
user asked for a full breakdown. The deep script was already available but not used.
This caused a second request and wasted time.

---

## RULE 0: Check Before You Create
Before writing any new scheduling script, ALWAYS check:
1. `marathon-agent/workout_generator.py` for running and cycling workouts.
2. `brain/.../scratch/schedule_strength_workout.py` for the strength/core pattern.
These are the canonical, battle-tested implementations. Reuse them.

---

## RULE 1: Running Workouts
**Command:** `python workout_generator.py <type> <duration_mins> --date YYYY-MM-DD --upload`

Available types: `easy`, `long_run`, `tempo`, `intervals`, `recovery`
Available intensities: `recovery`, `easy`, `marathon`, `threshold`, `vo2max`

### Examples:
```bash
# Recovery run, 40 mins, today
python workout_generator.py recovery 40 --date 2026-05-26 --upload

# Threshold intervals, 55 mins, tomorrow
python workout_generator.py intervals 55 --intensity threshold --date 2026-05-27 --upload

# Zone 2 easy, 50 mins
python workout_generator.py easy 50 --intensity easy --date 2026-05-28 --upload
```

---

## RULE 2: Cycling / Bike Workouts
**Same as running but add `--sport bike`.**

```bash
# Recovery spin, 40 mins
python workout_generator.py recovery 40 --sport bike --date 2026-05-26 --upload
```

The `--sport bike` flag triggers `CyclingWorkout` + `upload_cycling_workout` internally.
This is the ONLY correct way to schedule bike workouts. Never use a raw API payload.

---

## RULE 3: Strength / Core Workouts
**Use the `BaseWorkout` pattern.** The canonical reference implementation is:
`C:\Users\Max\.gemini\antigravity\brain\491e4690-66cd-499d-9776-017b0087dbe4\scratch\schedule_strength_workout.py`

### The Non-Negotiable Pattern:
```python
from garminconnect.workout import (
    BaseWorkout, WorkoutSegment, ExecutableStep,
    SportType, StepType, ConditionType, TargetType,
)

# Sport type for strength:
sportType = {"sportTypeId": 5, "sportTypeKey": "strength_training"}

# End conditions:
_REPS_CONDITION = {"conditionTypeId": 10, "conditionTypeKey": "reps", ...}
_TIME_CONDITION = {"conditionTypeId": 2,  "conditionTypeKey": "time", ...}

# Step types:
"interval" → StepType.INTERVAL  (work sets)
"rest"     → stepTypeId: 5      (rest between sets)

# Upload:
res = client.upload_workout(workout.model_dump())
workout_id = res.get("workoutId")
client.schedule_workout(workout_id, "YYYY-MM-DD")
```

### Key rules for strength workouts:
- Use `sportTypeId: 5` for strength_training. Do NOT use 13 or any other ID.
- Use `BaseWorkout`, NOT `RunningWorkout` or raw payload dicts.
- Timed exercises (planks, holds) → `_TIME_CONDITION` with `endConditionValue` in seconds.
- Rep-based exercises (dead bugs, RDLs) → `_REPS_CONDITION` with `endConditionValue` as float reps.
- Rest steps use `stepTypeId: 5` (rest), NOT StepType.RECOVERY.
- Always upload with `client.upload_workout(workout.model_dump())`.
- Always authenticate with `client.login(os.path.expanduser("~/.garminconnect"))` (cached token, not raw login).

---

## RULE 4: Garmin Authentication
ALWAYS use the cached token store, NOT a fresh email/password login.
Fresh logins trigger Garmin's `429 IP rate limiting`.

```python
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)
```

---

## RULE 5: When in Doubt, Check the Repo
If you are unsure whether a scheduling pattern exists, run:
```bash
dir scratch\
```
or look in:
`C:\Users\Max\.gemini\antigravity\brain\491e4690-66cd-499d-9776-017b0087dbe4\scratch\`

If a working script exists for the workout type you need, adapt IT — do not start from scratch.

---

## RULE 6: Sport Type IDs (Reference)
| Sport | sportTypeId | sportTypeKey |
|---|---|---|
| Running | 1 | running |
| Cycling | 2 | cycling |
| Strength Training | 5 | strength_training |
| Swimming | 4 | swimming |
| Walking | 9 | walking |

---

## SUMMARY TABLE
| Workout Type | Tool | Notes |
|---|---|---|
| Easy run, tempo, intervals, long run, recovery run | `workout_generator.py` | `--sport run` (default) |
| Cycling / bike | `workout_generator.py` | Must add `--sport bike` |
| Strength, core, plyometrics | Custom script using `BaseWorkout` | Use `schedule_strength_workout.py` as template |
| Cross-training (swim) | Custom script using `BaseWorkout` | sportTypeId: 4 |
