import os
import glob
from datetime import date, datetime, timezone, timedelta
import matplotlib.pyplot as plt
from google import genai
from dotenv import load_dotenv
from garminconnect import Garmin

# ── Timezone Anchor: ALL date/time logic must reference PHT (UTC+8) ──────────
# Max trains and lives in Marikina, Philippines. Never use UTC or local-system
# time naively — always derive from this constant.
PHT = timezone(timedelta(hours=8))

from physiological_engine import (
    PhysiologicalEngine,
    PhysiologicalReport,
    parse_sleep_data,
    parse_hrv_data,
    parse_activity_window,
    parse_laps,
)

# Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
garmin_email = os.getenv("GARMIN_EMAIL")
garmin_pass = os.getenv("GARMIN_PASSWORD")

TOKEN_STORE = os.path.expanduser("~/.garminconnect")

if not api_key:
    print("[ERROR] GEMINI_API_KEY not found. Please check your .env file.")
    exit()

def read_knowledge_base(directory="knowledge_base"):
    kb_content = ""
    if not os.path.exists(directory):
        print(f"[WARNING] Directory '{directory}' not found.")
        return "No rules loaded yet."
        
    for filepath in glob.glob(f"{directory}/*.md"):
        with open(filepath, 'r', encoding='utf-8') as file:
            kb_content += f"\n--- Source: {os.path.basename(filepath)} ---\n"
            kb_content += file.read()
    return kb_content

def fetch_live_telemetry():
    """Logs into Garmin Connect (PHT-anchored), fetches today's metrics, runs the
    Kiat Engine, and computes a Python-layer recovery context block.

    All date/time references use Philippine Time (PHT = UTC+8) explicitly.
    Recovery timing is computed to the HOUR using the exact workout end time
    (startTimeLocal + duration from Garmin telemetry) — not a coarse day count.
    The LLM receives 'hours_since_last_run_end' as a hard-computed float so it
    cannot misinterpret recency.

    Returns (telemetry_string, physiological_report, recovery_context_string).
    """
    print("[SYSTEM] Connecting to Garmin Connect...")

    # ── Anchor: today in PHT ───────────────────────────────────────────────────
    now_pht       = datetime.now(PHT)
    today_pht     = now_pht.date()
    today_label   = now_pht.strftime("%A, %B %d, %Y at %H:%M PHT")
    today_iso_pht = today_pht.isoformat()

    try:
        client = Garmin(
            email=garmin_email,
            password=garmin_pass,
            prompt_mfa=lambda: input("Garmin MFA code: "),
        )
        client.login(TOKEN_STORE)

        # ── Core biometrics ────────────────────────────────────────────────────
        summary   = client.get_user_summary(today_iso_pht)
        hrv_data  = client.get_hrv_data(today_iso_pht)
        sleep     = client.get_sleep_data(today_iso_pht)
        sleep_dto = sleep.get('dailySleepDTO', {})

        # Pull 35 activities (~30 days) for chronic workload
        activities = client.get_activities(0, 35)

        body_battery = summary.get('bodyBatteryMostRecentValue', 'N/A')
        rest_hr      = summary.get('restingHeartRate', 'N/A')
        stress_today = summary.get('averageStressLevel')

        hrv_7d, hrv_last = 'N/A', 'N/A'
        if hrv_data and 'hrvSummary' in hrv_data:
            hrv_7d   = hrv_data['hrvSummary'].get('weeklyAvg', 'N/A')
            hrv_last = hrv_data['hrvSummary'].get('lastNightAvg', 'N/A')

        # ── Last workout label ─────────────────────────────────────────────────
        last_workout = "No recent workouts found."
        if activities:
            act  = activities[0]
            name = act.get('activityName', 'Workout')
            dist = act.get('distance', 0) / 1000
            last_workout = (
                f"{name} ({dist:.2f} km) "
                f"- Avg HR: {act.get('averageHR', 'N/A')} bpm"
            )

        # ── Compute last RUNNING session: start, end, hours elapsed (all PHT) ──
        runs = [
            a for a in activities
            if a.get('activityType', {}).get('typeKey') == 'running'
        ]

        hours_since_last_run_end = None   # float — primary recovery signal
        last_run_start_label     = "N/A"
        last_run_end_label       = "N/A"
        last_run_duration_min    = 0.0
        last_run_name            = "N/A"
        last_run_dist_km         = 0.0
        last_run_avg_hr          = "N/A"
        last_recovery_hours      = None
        last_activity_end_utc    = None   # kept for TRS recovery-time scoring

        if runs:
            last_run = runs[0]
            last_run_name        = last_run.get('activityName', 'Run')
            last_run_dist_km     = last_run.get('distance', 0) / 1000
            last_run_avg_hr      = last_run.get('averageHR', 'N/A')
            last_recovery_hours  = last_run.get('recoveryTime')
            if last_recovery_hours:
                last_recovery_hours = float(last_recovery_hours)

            # Parse startTimeLocal as PHT (Garmin returns local wall-clock time)
            start_raw = last_run.get('startTimeLocal') or ''
            dur_secs  = float(last_run.get('duration') or 0)
            last_run_duration_min = dur_secs / 60.0

            if start_raw:
                try:
                    start_pht = datetime.fromisoformat(
                        start_raw[:19].replace(' ', 'T')
                    ).replace(tzinfo=PHT)
                    end_pht   = start_pht + timedelta(seconds=dur_secs)

                    last_run_start_label     = start_pht.strftime("%A, %B %d, %Y at %H:%M PHT")
                    last_run_end_label       = end_pht.strftime("%A, %B %d, %Y at %H:%M PHT")
                    hours_since_last_run_end = (now_pht - end_pht).total_seconds() / 3600.0

                    # Keep UTC end-time for TRS recovery-time scoring inside the engine
                    last_activity_end_utc = end_pht
                except ValueError:
                    pass

        # ── Python-layer recovery context — ground truth for the LLM ──────────
        # Computed from exact hours elapsed since last run ENDED (PHT timestamps).
        # The LLM is instructed not to override or reinterpret this block.
        if hours_since_last_run_end is None:
            recovery_context = "No running data available — recovery status unknown."

        elif hours_since_last_run_end < 6:
            recovery_context = (
                f"JUST FINISHED ({hours_since_last_run_end:.1f}h ago). "
                f"Last run '{last_run_name}' ({last_run_dist_km:.1f} km, "
                f"{last_run_duration_min:.0f} min) ended at {last_run_end_label}. "
                "Metabolic and structural recovery is in its earliest phase. "
                "Rule: Zone 1 or complete rest ONLY. No additional structured training today."
            )

        elif hours_since_last_run_end < 24:
            recovery_context = (
                f"WITHIN 24 HOURS ({hours_since_last_run_end:.1f}h since run ended). "
                f"Last run '{last_run_name}' ({last_run_dist_km:.1f} km, Avg HR {last_run_avg_hr} bpm) "
                f"ended at {last_run_end_label}. "
                "EPOC clearance is still in progress (estimated 40-70% cleared). "
                "Structural glycogen and micro-tear repair is ongoing. "
                "Rule: Zone 1-2 MAXIMUM regardless of distance. "
                "No Zone 3/4/5 or heavy lower-body lifting."
            )

        elif hours_since_last_run_end < 36:
            recovery_context = (
                f"24-36 HOURS POST-RUN ({hours_since_last_run_end:.1f}h since run ended). "
                f"Last run '{last_run_name}' ({last_run_dist_km:.1f} km, Avg HR {last_run_avg_hr} bpm) "
                f"ended at {last_run_end_label}. "
                "EPOC is approximately 70-85% cleared but structural repair is ongoing. "
                "Rule: Zone 2 is safe. Threshold (Zone 3-4) ONLY if last run was short "
                "(<15 km easy Zone 2). If last run was a long run (>18 km), hold at Zone 2."
            )

        elif hours_since_last_run_end < 48:
            recovery_context = (
                f"36-48 HOURS POST-RUN ({hours_since_last_run_end:.1f}h since run ended). "
                f"Last run '{last_run_name}' ({last_run_dist_km:.1f} km, Avg HR {last_run_avg_hr} bpm) "
                f"ended at {last_run_end_label}. "
                "EPOC is largely cleared (~85-95%). Structural recovery from normal long-run "
                "distances (18-25 km) is substantially complete. "
                "Rule: Threshold (Zone 3-4) is appropriate if HRV and TRS are green. "
                "VO2 Max (Zone 5) should only be prescribed if last run was <15 km and easy."
            )

        elif hours_since_last_run_end < 72:
            recovery_context = (
                f"48-72 HOURS POST-RUN ({hours_since_last_run_end:.1f}h since run ended). "
                f"Last run '{last_run_name}' ({last_run_dist_km:.1f} km) "
                f"ended at {last_run_end_label}. "
                "Full metabolic and structural recovery is complete for normal training loads. "
                "Rule: All session types (Zone 1-5) are appropriate — defer entirely to "
                "TRS, HRV, and ACWR gates for final prescription."
            )

        else:
            recovery_context = (
                f"EXTENDED REST ({hours_since_last_run_end:.1f}h / "
                f"{hours_since_last_run_end/24:.1f} days since run ended). "
                f"Last run: '{last_run_name}' ({last_run_dist_km:.1f} km) "
                f"ended at {last_run_end_label}. "
                "Full recovery is guaranteed. "
                "Risk: Detraining begins if gap exceeds 5+ days without cross-training. "
                "Rule: Resume with a moderate Zone 2 run to re-establish aerobic base signal."
            )

        # ── Run the Physiological Engine ───────────────────────────────────────
        phys_report = None
        try:
            engine     = PhysiologicalEngine()
            eng_sleep  = parse_sleep_data(sleep_dto)
            eng_hrv_d  = hrv_data.get('hrvSummary', {}) if hrv_data else {}
            eng_hrv    = parse_hrv_data(eng_hrv_d)
            eng_window = parse_activity_window(activities)

            # Fetch lap kinematics for last run
            eng_laps = []
            if runs:
                try:
                    splits = client.get_activity_splits(runs[0].get('activityId'))
                    if splits and 'lapDTOs' in splits:
                        eng_laps = parse_laps(splits['lapDTOs'])
                except Exception:
                    pass

            phys_report = engine.compute(
                sleep=eng_sleep,
                hrv=eng_hrv,
                recovery_hours=last_recovery_hours,
                activity_end_time_utc=last_activity_end_utc,
                rolling_stress_3d=float(stress_today) if stress_today else None,
                activity_window=eng_window,
                laps=eng_laps if eng_laps else None,
            )
            print("[SYSTEM] Physiological engine computed successfully.")
        except Exception as eng_err:
            print(f"[WARNING] Physiological engine failed: {eng_err}")

        # ── Format core telemetry string ───────────────────────────────────────
        hrs_display = (
            f"{hours_since_last_run_end:.1f}h"
            if hours_since_last_run_end is not None else "Unknown"
        )
        telemetry = f"""
        TODAY (PHT):              {today_label}
        ----------------------------------------------------------------
        - 7-Day HRV Avg:          {hrv_7d} ms
        - Last Night HRV:         {hrv_last} ms
        - Waking Body Battery:    {body_battery}/100
        - Resting HR:             {rest_hr} bpm
        - Today's Stress:         {stress_today if stress_today is not None else 'N/A'}
        ----------------------------------------------------------------
        LAST RUN (computed in Python — authoritative, PHT timestamps):
        - Run Name:               {last_run_name}
        - Distance:               {last_run_dist_km:.2f} km | Avg HR: {last_run_avg_hr} bpm
        - Started:                {last_run_start_label}
        - Ended:                  {last_run_end_label}
        - Duration:               {last_run_duration_min:.0f} min
        - Hours Since Run Ended:  {hrs_display}  ← PRIMARY RECOVERY SIGNAL
        - Last Activity (any):    {last_workout}
        """
        print("[SYSTEM] Live telemetry successfully acquired.")
        return telemetry, phys_report, recovery_context

    except Exception as e:
        print(f"[ERROR] Garmin Sync Failed: {e}")
        return "Garmin data unavailable.", None, "Recovery context unavailable — Garmin sync failed."

def get_agent_recommendation(kb_context, daily_metrics, phys_report=None, recovery_context=""):
    client = genai.Client(api_key=api_key)

    # ── Physiological engine block ─────────────────────────────────────────────
    if phys_report is not None:
        phys_block = phys_report.summary_text
        veto_directive = (
            "\n    ⛔ MANDATORY SPEED VETO: ACWR > 1.5 has been detected. You MUST output "
            "NO-GO for all high-intensity work today (intervals, tempo, VO2Max, heavy "
            "lower-body lifting). The only permitted sessions are Zone 1/2 easy runs, "
            "cycling, or complete rest."
            if phys_report.speed_veto
            else ""
        )
    else:
        phys_block = "Physiological engine data unavailable for this session."
        veto_directive = ""

    prompt = f"""
    You are 'Antigravity' — an autonomous running coach for Max, a 25yo elite-amateur
    marathon runner in Marikina, Philippines, powered by the Kiat Engine physiological
    intelligence layer.

    ══════════════════════════════════════════════════════════════════
    ATHLETE PROFILE
    ══════════════════════════════════════════════════════════════════
    Age: 25 | Weight: 75.5 kg | Height: 175 cm
    Max HR: 206 bpm | LTHR: 190-196 bpm | Resting HR: 38-42 bpm
    HRV Floor: 116 ms RMSSD — non-negotiable recovery gate.
    Zone 2 Cap: 162 bpm (heat-tax adjusted for Marikina tropical conditions).
    HR Zones: Z1 <145 | Z2 145-162 | Z3 163-184 | Z4 185-196 | Z5 197+
    Training Phase: Perpetual Base / No-Race State.
      - 80/20 rule enforced: 80% Zone 2, 20% quality.
      - Max 1 hard running session per week.
      - Long run cap: 21.1-25 km.
      - ACWR target: 0.9-1.15 (sweet spot).
    Environment: 27C+ and humid. Cardiac drift is expected on all outdoor runs.

    ══════════════════════════════════════════════════════════════════
    LIVE TELEMETRY — Pulled from Garmin just now
    ══════════════════════════════════════════════════════════════════
    {daily_metrics}

    ══════════════════════════════════════════════════════════════════
    KIAT ENGINE — PHYSIOLOGICAL METRICS (Computed this session)
    ══════════════════════════════════════════════════════════════════
    {phys_block}

    ══════════════════════════════════════════════════════════════════
    PYTHON-COMPUTED RECOVERY CONTEXT — Use this as ground truth.
    Do NOT reinterpret or override this block. It is pre-computed
    from exact Philippine Time (PHT) timestamps by the Python layer.
    ══════════════════════════════════════════════════════════════════
    {recovery_context}
    {veto_directive}

    ══════════════════════════════════════════════════════════════════
    KIAT ENGINE PRIORITY STACK — Follow in strict order
    ══════════════════════════════════════════════════════════════════
    P1 [Override All]: ACWR > 1.5 → Speed Veto. No debate.
    P2 [Hard Gate]:    HRV < 116 ms → No Zone 4/5 or heavy lower-body.
    P3 [Recovery Gate]:Hours Since Last Run ENDED (from Python-Computed block).
       Use 'Hours Since Run Ended' from telemetry as the authoritative value.
       < 6h   → Zone 1 or complete rest ONLY. No further sessions today.
       6-24h  → Zone 1-2 MAXIMUM. No Zone 3/4/5 regardless of HRV/TRS.
       24-36h → Zone 2 safe. Zone 3-4 ONLY if last run was <15 km easy.
               If last run was >18 km, hold at Zone 2.
       36-48h → Zone 3-4 (Threshold) appropriate if HRV ≥ 116 ms and TRS green.
               Zone 5 (VO2 Max) ONLY if last run was <15 km and easy.
       48-72h → All zones permitted, gated only by TRS, HRV, and ACWR.
       > 72h  → Full clearance. Warn about detraining if gap > 5 days.
    P4 [Advisory]:     TRS < 50 → Downgrade all sessions to Zone 2 max.
    P5 [Biomechanics]: FBI < 70 → Shorten session and add mobility work.
    P6 [Standard]:     Training Status guides periodisation prescription.

    ══════════════════════════════════════════════════════════════════
    KNOWLEDGE BASE OPERATING RULES
    ══════════════════════════════════════════════════════════════════
    {kb_context}

    ══════════════════════════════════════════════════════════════════
    YOUR OUTPUT TASK
    ══════════════════════════════════════════════════════════════════
    Using ALL of the above — in strict Priority Stack order — produce:

    1. GO / NO-GO status for HIGH-INTENSITY work today.
       - Cite the SPECIFIC metric and its value that drives the decision.
       - ALWAYS state 'Hours Since Last Run Ended' explicitly (e.g. '41.3h').
       - Map that value to the correct P3 Recovery Gate tier.

    2. TRAINING STATUS — State it and explain the metric combination that
       produced it (ACWR value + HRV value + hours since last run ended).

    3. REI & FBI commentary — Flag any form collapse or economy regression.
       If data is N/A, say so — do not speculate.

    4. TODAY'S SESSION RECOMMENDATION — One specific, actionable paragraph.
       Include: session type, target HR zone, target duration/distance,
       and the exact metric that justifies the prescription.
       Do NOT recommend a session type that contradicts the Priority Stack.

    5. RECOVERY OUTLOOK — Brief statement on what tomorrow's session window
       will look like based on today's prescription.

    Be clinical and direct. Do NOT hallucinate data. If a metric is N/A,
    acknowledge it and state what you would need to compute it.
    """

    print("[SYSTEM] Consulting the Brain...\n")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

if __name__ == "__main__":
    # 1. Read the Rulebook
    kb_data = read_knowledge_base()

    # 2. Fetch LIVE Garmin Data + run Physiological Engine
    #    Returns three values now: telemetry string, phys report, recovery context
    live_telemetry, phys_report, recovery_ctx = fetch_live_telemetry()

    # 3. Get the Recommendation
    verdict = get_agent_recommendation(
        kb_data, live_telemetry, phys_report, recovery_ctx
    )

    print("========================================")
    print("      ANTIGRAVITY DAILY BRIEFING        ")
    print("========================================\n")
    print(live_telemetry)
    print("\n-- PYTHON-COMPUTED RECOVERY CONTEXT ----")
    print(recovery_ctx)
    if phys_report:
        print(phys_report.summary_text)
    print("----------------------------------------")
    print(verdict)