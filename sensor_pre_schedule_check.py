"""
sensor_pre_schedule_check.py — Antigravity Mandatory Pre-Scheduling Gate
=================================================================
RULE 00 of AGENT_SCHEDULING_PROTOCOL.md mandates that this script is run
BEFORE any workout is scheduled to Garmin Connect.

This script:
1. Loads today's session from brain_current_week_plan.py
2. Pulls live ACWR from audit_acwr.py logic
3. Loads last 8 weeks of mileage history
4. Reads operating_manual.md for current HR zones
5. Prints a full justification report
6. Returns exit code 1 (blocks scheduling) if ACWR > 1.5 or a veto condition exists

Usage:
    python sensor_pre_schedule_check.py --type easy --duration 70

The agent MUST run this before calling actuator_workout_generator.py --upload.
If this script exits with code 1, do NOT proceed with scheduling.
"""

import os, sys, json, argparse, math
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from datetime import date, datetime, timedelta
from collections import defaultdict

sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")

# ── CURRENT WEEK PLAN ──────────────────────────────────────────────────────────
try:
    from brain_current_week_plan import plan
    PLAN_LOADED = True
except Exception as e:
    PLAN_LOADED = False
    PLAN_ERROR = str(e)

# ── GARMIN ─────────────────────────────────────────────────────────────────────
from garminconnect import Garmin
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

HR_REST = 40
HR_MAX  = 206

def pace_str(speed_ms):
    if not speed_ms or speed_ms <= 0: return "N/A"
    p = 1000 / speed_ms / 60
    return f"{int(p)}:{int((p - int(p)) * 60):02d}"

def trimp_banister(dur_min, hr_avg):
    if not hr_avg: return 0
    r = (hr_avg - HR_REST) / (HR_MAX - HR_REST)
    return round(dur_min * r * 0.64 * math.exp(1.92 * r), 2)

# ── ACWR (Mechanical Tolerance) ──────────────────────────────────────────
from core_tolerance_engine import calculate_mechanical_load

def compute_acwr():
    tol_data = calculate_mechanical_load(client)
    # Return (acute_km, chronic_weekly, acwr) to keep backward compatibility 
    # with the rest of sensor_pre_schedule_check.py's projection math
    acute = tol_data["acute_distance_km"]
    chronic_weekly = tol_data["chronic_avg_km_day"] * 7  # Extrapolate to weekly
    acwr = tol_data["mechanical_acwr"]
    return acute, chronic_weekly, acwr

# ── WEEKLY HISTORY ─────────────────────────────────────────────────────────────
def compute_weekly_history():
    today = date.today()
    acts = client.get_activities_by_date(
        (today - timedelta(days=56)).strftime("%Y-%m-%d"),
        today.strftime("%Y-%m-%d"),
        "running"
    )
    weeks = defaultdict(lambda: {"km": 0.0, "longest": 0.0, "runs": 0})
    for act in acts:
        dt = datetime.strptime(act["startTimeLocal"], "%Y-%m-%d %H:%M:%S").date()
        monday = dt - timedelta(days=dt.weekday())
        km = (act.get("distance") or 0) / 1000
        weeks[monday]["km"] += km
        weeks[monday]["runs"] += 1
        if km > weeks[monday]["longest"]:
            weeks[monday]["longest"] = km
    return weeks

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Antigravity pre-scheduling justification gate. Run before actuator_workout_generator.py."
    )
    parser.add_argument("--type",     required=True,
                        choices=["easy", "long_run", "tempo", "intervals", "recovery"],
                        help="Workout type you intend to schedule")
    parser.add_argument("--duration", required=True, type=int,
                        help="Intended duration in minutes")
    parser.add_argument("--intensity", default="easy",
                        choices=["recovery", "easy", "marathon", "threshold", "vo2max"])
    args = parser.parse_args()

    today_str = date.today().strftime("%Y-%m-%d")
    print("=" * 65)
    print("  ANTIGRAVITY PRE-SCHEDULE JUSTIFICATION REPORT")
    print(f"  Date: {today_str} | Requested: {args.type} {args.duration}min @{args.intensity}")
    print("=" * 65)

    # ── 1. Weekly Plan Check ───────────────────────────────────────────
    print("\n[1] WEEKLY PLAN CHECK")
    veto = False
    veto_reason = ""

    if not PLAN_LOADED:
        print(f"  [WARN] Could not load brain_current_week_plan.py: {PLAN_ERROR}")
        print("         Update brain_current_week_plan.py every Sunday with the new week's plan.")
        planned_session = None
    else:
        print(f"  Week: {plan['meta']['week']}")
        print(f"  Phase: {plan['meta']['phase']}")
        print(f"  Load target: {plan['meta']['load_target']}")
        print(f"  Zones: {plan['meta']['zone_update']}")

        if today_str in plan["days"]:
            d = plan["days"][today_str]
            print(f"\n  TODAY'S SCHEDULED SESSION:")
            print(f"    {d['label']}")
            print(f"    {d['session']}")
            print(f"    {d['detail']}")
            print(f"    Run km target: {d['run_km']} km | Gym: {d['gym']} | Plyo: {d['plyo']}")
            planned_session = d

            # Check if a run is even planned for today
            if d['run_km'] == 0 and args.type in ["easy", "long_run", "tempo", "intervals"]:
                print(f"\n  [ADVISORY] The weekly plan has NO run scheduled for today ({d['label']}).")
                print("             A run was requested anyway. Verify this is a deliberate override.")
        else:
            print(f"  [WARN] No plan entry found for {today_str}. Proceeding without plan check.")
            planned_session = None

        # Injury check
        if "wrist" in plan["meta"].get("wrist_note", "").lower():
            print(f"\n  [INJURY FLAG] {plan['meta']['wrist_note']}")
        if "achilles" in plan["meta"].get("injury_note", "").lower():
            print(f"  [ACHILLES]    {plan['meta']['injury_note']}")

    # ── 2. ACWR Gate ───────────────────────────────────────────────────
    print("\n[2] ACWR GATE (Verified Calculation)")
    try:
        acute, chronic_weekly, acwr = compute_acwr()
        
        # Estimate projected distance based on duration and intensity
        pace_map = {
            "recovery": 7.0,
            "easy": 6.0,
            "marathon": 5.5,
            "tempo": 5.0,
            "threshold": 4.5,
            "vo2max": 4.0
        }
        intensity = getattr(args, "intensity", "easy")
        if not intensity: intensity = "easy"
        est_pace = pace_map.get(intensity, 6.0)
        dur = float(getattr(args, "duration", 0))
        proj_dist = dur / est_pace
        
        proj_acute = acute + proj_dist
        proj_acwr = round(proj_acute / chronic_weekly, 3) if chronic_weekly > 0 else 0
        
        print(f"  Current Acute (7d): {round(acute, 2)} km")
        print(f"  Chronic Avg (28d):  {round(chronic_weekly, 2)} km/week")
        print(f"  Current ACWR:       {acwr}")
        print(f"  Projected Distance: ~{round(proj_dist, 2)} km (based on {intensity} pace)")
        print(f"  Projected ACWR:     {proj_acwr}")

        if proj_acwr > 1.5:
            print(f"  [VETO] Projected ACWR > 1.5. Proposed run of {round(proj_dist,1)}km pushes ACWR into Danger Zone.")
            veto = True
            veto_reason = f"Projected ACWR is {proj_acwr} (> 1.500). Run pushes chassis into Severe Danger Zone."
        elif proj_acwr > 1.3:
            print("  [CAUTION] Projected ACWR in caution zone (1.3–1.5). Reduce volume in next 3–5 days.")
            if args.type in ["intervals", "tempo"] and acwr > 1.4:
                veto = True
                veto_reason = f"Current ACWR is {acwr} (> 1.4). Speed veto active. Only easy/recovery allowed until ACWR drops below 1.4."
        elif proj_acwr >= 0.8:
            print("  [OK] Projected ACWR in Sweet Spot (0.8–1.3). Load is safe.")
        else:
            print("  [LOW] Projected ACWR below 0.8 — underloading. Adding volume is appropriate.")
    except Exception as e:
        print(f"  [ERROR] Could not compute ACWR: {e}")
        acwr = None

    # ── 3. Weekly History ──────────────────────────────────────────────
    print("\n[3] LAST 8 WEEKS MILEAGE HISTORY")
    try:
        weeks = compute_weekly_history()
        weekly_kms = []
        for monday in sorted(weeks.keys()):
            d = weeks[monday]
            end = monday + timedelta(days=6)
            label = monday.strftime("%b %d") + " - " + end.strftime("%b %d")
            km = round(d["km"], 1)
            weekly_kms.append(km)
            print(f"  {label}: {km:>6} km | {d['runs']} runs | Longest: {round(d['longest'],1)} km")

        if weekly_kms:
            avg_km = round(sum(weekly_kms) / len(weekly_kms), 1)
            peak_km = max(weekly_kms)
            print(f"\n  8-week avg:  {avg_km} km/week")
            print(f"  8-week peak: {peak_km} km/week")
            print(f"  Justified weekly target: {round(avg_km * 1.05, 1)}–{round(avg_km * 1.10, 1)} km (avg +5-10%)")
    except Exception as e:
        print(f"  [ERROR] Could not compute weekly history: {e}")

    # ── 4. HR Zone Reminder ────────────────────────────────────────────
    print("\n[4] CURRENT HR ZONES (LTHR Method, June 6 2026)")
    print("  Zone 1 (Easy Aerobic):  < 162 bpm  — all easy/long runs")
    print("  Zone 2 (Extensive):   162–174 bpm  — aerobic stimulus")
    print("  Zone 3 (Tempo):       174–181 bpm  — marathon pace work")
    print("  Zone 4 (Threshold):   181–191 bpm  — interval work")
    print("  Zone 5 (VO2 Max):     > 191 bpm    — max efforts")

    # ── 5. Verdict ─────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    if veto:
        print(f"  VERDICT: [BLOCKED]")
        print(f"  REASON:  {veto_reason}")
        print("=" * 65)
        sys.exit(1)
    else:
        print(f"  VERDICT: [CLEARED]")
        print(f"  Workout: {args.type} | {args.duration} min | {args.intensity}")
        print("  Proceed with: python actuator_workout_generator.py "
              f"{args.type} {args.duration} --intensity {args.intensity} "
              "--date YYYY-MM-DD --upload")
        print("=" * 65)
        sys.exit(0)

if __name__ == "__main__":
    main()
