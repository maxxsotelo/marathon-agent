import os
import glob
from datetime import date, datetime, timezone, timedelta
import matplotlib.pyplot as plt
from google import genai
from dotenv import load_dotenv
from garminconnect import Garmin

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
    """Logs into Garmin, fetches today's metrics, and runs the physiological engine.
    Returns (telemetry_string, physiological_report).
    """
    print("[SYSTEM] Connecting to Garmin Connect...")
    try:
        client = Garmin(
            email=garmin_email,
            password=garmin_pass,
            prompt_mfa=lambda: input("Garmin MFA code: "),
        )
        client.login(TOKEN_STORE)
        today = date.today().isoformat()

        # ── Core biometrics ────────────────────────────────────────────
        summary  = client.get_user_summary(today)
        hrv_data = client.get_hrv_data(today)
        sleep    = client.get_sleep_data(today)
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

        last_workout = "No recent workouts found."
        if activities:
            act = activities[0]
            name = act.get('activityName', 'Workout')
            dist = act.get('distance', 0) / 1000
            last_workout = f"{name} ({dist:.2f} km) - Avg HR: {act.get('averageHR', 'N/A')} bpm"

        # ── Run the Physiological Engine ───────────────────────────────
        phys_report = None
        try:
            engine = PhysiologicalEngine()

            eng_sleep  = parse_sleep_data(sleep_dto)
            eng_hrv_d  = hrv_data.get('hrvSummary', {}) if hrv_data else {}
            eng_hrv    = parse_hrv_data(eng_hrv_d)
            eng_window = parse_activity_window(activities)

            # Resolve last run recovery hours + end-time
            runs = [a for a in activities if a.get('activityType', {}).get('typeKey') == 'running']
            last_recovery_hours   = None
            last_activity_end_utc = None
            if runs:
                last_run = runs[0]
                last_recovery_hours = last_run.get('recoveryTime')
                if last_recovery_hours:
                    last_recovery_hours = float(last_recovery_hours)
                start_raw    = last_run.get('startTimeLocal') or ''
                dur_secs     = last_run.get('duration') or 0
                if start_raw:
                    try:
                        dt_naive = datetime.fromisoformat(start_raw[:19].replace(' ', 'T'))
                        start_utc = dt_naive.replace(tzinfo=timezone.utc) - timedelta(hours=8)
                        last_activity_end_utc = start_utc + timedelta(seconds=dur_secs)
                    except ValueError:
                        pass

            # Fetch lap kinematics for last run (REI/FBI)
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

        # ── Format core telemetry string ───────────────────────────────
        telemetry = f"""
        - 7-Day HRV Avg:      {hrv_7d} ms
        - Last Night HRV:     {hrv_last} ms
        - Waking Body Battery:{body_battery}/100
        - Resting HR:         {rest_hr} bpm
        - Last Logged Workout:{last_workout}
        - Today's Stress:     {stress_today if stress_today is not None else 'N/A'}
        """
        print("[SYSTEM] Live telemetry successfully acquired.")
        return telemetry, phys_report

    except Exception as e:
        print(f"[ERROR] Garmin Sync Failed: {e}")
        return "Garmin data unavailable.", None

def get_agent_recommendation(kb_context, daily_metrics, phys_report=None):
    client = genai.Client(api_key=api_key)

    # ── Physiological engine block ─────────────────────────────────────────
    if phys_report is not None:
        phys_block = phys_report.summary_text
        veto_directive = (
            """\n
    ⛔ MANDATORY SPEED VETO: ACWR > 1.5 has been detected. You MUST output NO-GO for all
    high-intensity work today (intervals, tempo, VO2Max, heavy lower-body lifting).
    The only permitted sessions are Zone 1/2 easy runs, cycling, or complete rest."""
            if phys_report.speed_veto
            else ""
        )
    else:
        phys_block = "Physiological engine data unavailable for this session."
        veto_directive = ""

    prompt = f"""
    You are 'Antigravity', an autonomous running coach powered by the Kiat Engine --
    a custom physiological intelligence layer (Hokkien: Kiat = to surpass) that computes
    premium coaching metrics beyond the capability of the athlete's Garmin Forerunner 165.

    ATHLETE PROFILE:
    - Fast-twitch dominant (mesomorph) transitioned to distance running.
    - Age: 25 | Weight: 75.5 kg | Height: 175 cm
    - Max HR: 206 bpm | LTHR: 190–196 bpm | Resting HR: ~38–42 bpm
    - HRV Floor: 116 ms RMSSD (non-negotiable recovery gate).
    - Zone 2 Cap: 162 bpm (heat-tax adjusted for Marikina tropical conditions).
    - Environment: 27°C+ and humid. Cardiac drift is expected on all outdoor runs.

    OPERATING RULES (From Knowledge Base):
    {kb_context}
    {veto_directive}

    LIVE TELEMETRY (Pulled from Garmin just now):
    {daily_metrics}

    KIAT ENGINE -- PHYSIOLOGICAL METRICS (Computed this session):
    {phys_block}

    YOUR TASK:
    Analyze the live telemetry AND the premium physiological metrics strictly against the
    Operating Rules.
    1. Output a GO / NO-GO status for high-intensity work today. Cite the specific metric
       that drives this decision (e.g., "HRV at X ms is below the 116 ms floor").
    2. State the current Training Status (Productive, Peaking, Strained, Maintaining,
       Recovery, or Unproductive) and explain why.
    3. Comment on Running Economy (REI) and Biomechanical Integrity (FBI) if data is
       available. Flag any form collapse or economy regression.
    4. Provide a specific, 1-paragraph training recommendation for today's session based
       on the actual data provided above. Include target HR zone and duration.
    5. Be clinical and direct. Do NOT hallucinate data. If a metric is N/A, acknowledge it.
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
    live_telemetry, phys_report = fetch_live_telemetry()

    # 3. Get the Recommendation
    verdict = get_agent_recommendation(kb_data, live_telemetry, phys_report)

    print("========================================")
    print("      ANTIGRAVITY DAILY BRIEFING        ")
    print("========================================\n")
    print(live_telemetry)
    if phys_report:
        print(phys_report.summary_text)
    print("----------------------------------------")
    print(verdict)