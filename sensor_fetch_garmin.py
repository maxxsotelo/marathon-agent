import os
from datetime import date, datetime, timezone, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin

from core_physiological_engine import (
    PhysiologicalEngine,
    parse_sleep_data,
    parse_hrv_data,
    parse_activity_window,
    parse_laps,
)

load_dotenv()
email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

# Token store path — credentials saved here after first login.
# Subsequent runs load tokens automatically; no MFA prompt needed.
TOKEN_STORE = os.path.expanduser("~/.garminconnect")

# Helper function to cleanly round Garmin's raw floating point data
def f_num(val, dec=0):
    if val is None or val == 'N/A': return 'N/A'
    try: return f"{float(val):.{dec}f}"
    except: return val

# Helper to convert speed (m/s) to pace (min/km)
def get_pace(speed_ms):
    if not speed_ms or speed_ms <= 0: return "N/A"
    total_seconds = 1000 / speed_ms
    return f"{int(total_seconds // 60)}:{int(total_seconds % 60):02d}"

def run_sync():
    try:
        client = Garmin(
            email=email,
            password=password,
            prompt_mfa=lambda: input("Garmin MFA code: "),
        )
        # Load saved tokens if they exist; fall back to full login + save.
        client.login(TOKEN_STORE)
        today = date.today().isoformat()
        
        print("=== AT A GLANCE: HEALTH & RECOVERY ===")
        
        # 1. BIOMETRICS
        body_data = client.get_body_composition(today)
        print(f"Weight: {body_data.get('totalWeight', 'N/A')} kg")

        # 2. USER SUMMARY
        summary = client.get_user_summary(today)
        print(f"Body Battery: {summary.get('bodyBatteryMostRecentValue', 'N/A')}/100")
        print(f"Resting HR: {summary.get('restingHeartRate', 'N/A')} bpm")
        print(f"Stress Score: {summary.get('averageStressLevel', 'N/A')}")
        
        # Intensity Minutes for the day
        print(f"Intensity:    Moderate {summary.get('moderateIntensityMinutes', 0)}m | Vigorous {summary.get('vigorousIntensityMinutes', 0)}m")

        # 3. SLEEP & HRV
        sleep = client.get_sleep_data(today)
        sleep_dto = sleep.get('dailySleepDTO', {})
        print(f"Sleep Score: {sleep_dto.get('sleepScore', 'N/A')}")
        
        # Total sleep duration
        total_sleep_secs = sleep_dto.get('sleepTimeInSeconds') or sleep_dto.get('totalSleepSeconds') or 0
        if total_sleep_secs:
            sleep_h, sleep_rem = divmod(int(total_sleep_secs), 3600)
            sleep_m = sleep_rem // 60
            print(f"Sleep Duration: {sleep_h}h {sleep_m}m")
        else:
            print("Sleep Duration: N/A")

        # Sleep stage breakdowns
        deep_secs  = sleep_dto.get('deepSleepSeconds', 0) or sleep_dto.get('deepSleepDurationInSeconds', 0) or 0
        light_secs = sleep_dto.get('lightSleepSeconds', 0) or sleep_dto.get('lightSleepDurationInSeconds', 0) or 0
        rem_secs   = sleep_dto.get('remSleepSeconds', 0) or sleep_dto.get('remSleepInSeconds', 0) or 0
        awake_secs = sleep_dto.get('awakeSleepSeconds', 0) or sleep_dto.get('awakeDurationInSeconds', 0) or 0

        def fmt_sleep(secs):
            if not secs: return "0h 0m"
            h, r = divmod(int(secs), 3600)
            m = r // 60
            return f"{h}h {m:02d}m"

        def pct(part, whole):
            if not whole: return "0"
            return f"{(part / whole) * 100:.0f}"

        stage_total = deep_secs + light_secs + rem_secs + awake_secs
        ref_total = total_sleep_secs if total_sleep_secs else stage_total
        if ref_total:
            print(f"  Deep:  {fmt_sleep(deep_secs)}  ({pct(deep_secs, ref_total)}%)")
            print(f"  Light: {fmt_sleep(light_secs)}  ({pct(light_secs, ref_total)}%)")
            print(f"  REM:   {fmt_sleep(rem_secs)}  ({pct(rem_secs, ref_total)}%)")
            print(f"  Awake: {fmt_sleep(awake_secs)}  ({pct(awake_secs, ref_total)}%)")
        
        hrv_data = client.get_hrv_data(today)
        if hrv_data and 'hrvSummary' in hrv_data:
            hrv_7d = hrv_data['hrvSummary'].get('weeklyAvg', 'N/A')
            hrv_last_night = hrv_data['hrvSummary'].get('lastNightAvg', 'N/A')
            print(f"HRV Status (7d Avg): {hrv_7d} ms")
            print(f"Last Night HRV: {hrv_last_night} ms")

        # 3.5 NUTRITION (via MyFitnessPal → Garmin Connect sync)
        print("\n--- Nutrition (MyFitnessPal Sync) ---")
        mfp_synced    = summary.get('includesCalorieConsumedData', False)
        consumed_kcal = summary.get('consumedKilocalories') or 0
        calorie_goal  = summary.get('netCalorieGoal') or 0
        remaining     = summary.get('remainingKilocalories') or summary.get('netRemainingKilocalories') or 0
        burned_active = summary.get('activeKilocalories') or 0
        burned_total  = summary.get('totalKilocalories') or 0

        if not mfp_synced or consumed_kcal == 0:
            # No food data found — don't make assumptions, just ask
            print("  ⚠️  No food log found for today (yet).")
            print("  → Did you forget to log your meals in MyFitnessPal?")
            print("     If yes, log them and re-run this script to see your nutrition balance.")
            print("     If you haven't eaten yet, that's fine — check back after your first meal.")
        else:
            # Net balance: consumed minus total calories burned (BMR + active)
            net_balance  = consumed_kcal - burned_total
            balance_label = "SURPLUS" if net_balance > 0 else "DEFICIT"

            print(f"  Consumed:     {consumed_kcal:.0f} kcal")
            print(f"  Daily Goal:   {calorie_goal:.0f} kcal")
            print(f"  Remaining:    {remaining:.0f} kcal left to goal")
            print(f"  Active Burn:  {burned_active:.0f} kcal (from exercise)")
            print(f"  Total Burn:   {burned_total:.0f} kcal (BMR + active)")
            print(f"  Net Balance:  {net_balance:+.0f} kcal ({balance_label})")

        # 4. RECENT WORKOUTS — Expanded to 35 activities (~30 days) for ACWR
        print("\n=== RECENT WORKOUTS (LAST 30 DAYS) ===")
        activities = client.get_activities(0, 35)
        for act in activities[:10]:   # Print only the 10 most recent for readability
            name = act.get('activityName', 'Workout')
            dist = act.get('distance', 0) / 1000
            start = act.get('startTimeLocal', 'N/A')[:10]
            print(f" - {start} | {name} ({dist:.2f} km)")
        if len(activities) > 10:
            print(f"   ... and {len(activities) - 10} more activities in the 30-day window (used for ACWR)")

        # 5. DEEP DIVE: POST-WORKOUT AUDIT
        print("\n=== DEEP DIVE: POST-WORKOUT AUDIT ===")
        
        # --- RUNNING ---
        runs = [a for a in activities if a['activityType']['typeKey'] == 'running']
        if runs:
            last_run = runs[0]
            act_id = last_run.get('activityId')
            
            print(f"[ RUN ] {last_run.get('activityName')}")
            print(f"  - Distance: {last_run.get('distance', 0) / 1000:.2f} km")
            print(f"  - Avg Pace: {get_pace(last_run.get('averageSpeed'))} /km")
            print(f"  - GAP:      {get_pace(last_run.get('avgGradeAdjustedSpeed'))} /km (Grade Adjusted)")
            print(f"  - Heart Rate: {f_num(last_run.get('averageHR'), 0)} avg / {f_num(last_run.get('maxHR'), 0)} max")
            
            # Load & Classification
            print("\n  [ Benefit & Recovery ]")
            print(f"    - Primary Benefit: {last_run.get('trainingEffectLabel', 'N/A')}")
            print(f"    - Training Effect: Aerobic {f_num(last_run.get('aerobicTrainingEffect'), 1)} | Anaerobic {f_num(last_run.get('anaerobicTrainingEffect'), 1)}")
            print(f"    - Training Load:   {f_num(last_run.get('activityTrainingLoad'), 0)}")
            
            # Garmin Recovery hours (if available in summary)
            rec_hours = last_run.get('recoveryTime', 'N/A')
            print(f"    - Recovery Time:   {rec_hours} hours")

            # Environment & Elevation
            print("\n  [ Environment & Elevation ]")
            print(f"    - Elevation:       +{f_num(last_run.get('elevationGain'), 0)}m / -{f_num(last_run.get('elevationLoss'), 0)}m")
            print(f"    - Temp (C):        Avg {f_num(last_run.get('avgTemperature'), 1)} | Max {f_num(last_run.get('maxTemperature'), 1)}")

            # Mechanics & Dynamics
            print("\n  [ Dynamics & Subjective ]")
            stride_raw = last_run.get('avgStrideLength', last_run.get('averageStrideLength'))
            stride_m = f"{float(stride_raw)/100:.2f}" if (stride_raw and float(stride_raw) > 10) else f_num(stride_raw, 2)
            
            print(f"    - Mechanics:       {f_num(last_run.get('averageRunningCadenceInStepsPerMinute'), 0)} spm | {stride_m} m stride")
            print(f"    - Vertical:        Osc {f_num(last_run.get('avgVerticalOscillation'), 1)} cm | Ratio {f_num(last_run.get('avgVerticalRatio'), 1)} %")
            print(f"    - Self-Eval:       Feel: {last_run.get('userSelfEvaluation', 'N/A')} | RPE: {last_run.get('userPerceivedEffort', 'N/A')}/10")

            try:
                # ---- Per-Lap / Per-Interval Full Breakdown ----------------
                # Athlete weight for W/kg calculations (update when weight changes)
                ATHLETE_WEIGHT_KG = 74.0

                def fmt_time(secs):
                    m, s = divmod(int(secs), 60)
                    h, m = divmod(m, 60)
                    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

                splits = client.get_activity_splits(act_id)
                if splits and 'lapDTOs' in splits:
                    laps = splits['lapDTOs']
                    print(f"\n  [ Interval Breakdown - {len(laps)} laps ]")
                    for lap in laps:
                        lap_num   = lap.get('lapIndex', '?')
                        intensity = lap.get('intensityType', 'ACTIVE')
                        phase_label = {
                            'WARMUP':   '[WU]  Warm-Up',
                            'ACTIVE':   '[ACT] Active',
                            'COOLDOWN': '[CD]  Cool-Down',
                            'REST':     '[RST] Rest',
                        }.get(intensity, f'      {intensity}')

                        # -- Distance & Time ---------------------------------
                        dist_km      = (lap.get('distance') or 0) / 1000
                        moving_secs  = lap.get('movingDuration') or 0

                        # -- Pace --------------------------------------------
                        avg_pace     = get_pace(lap.get('averageSpeed'))
                        moving_pace  = get_pace(lap.get('averageMovingSpeed'))
                        best_pace    = get_pace(lap.get('maxSpeed'))
                        gap_pace     = get_pace(lap.get('avgGradeAdjustedSpeed'))

                        # -- Heart Rate --------------------------------------
                        avg_hr       = f_num(lap.get('averageHR'), 0)
                        max_hr       = f_num(lap.get('maxHR'), 0)

                        # -- Elevation ---------------------------------------
                        elev_gain    = f_num(lap.get('elevationGain'), 0)
                        elev_loss    = f_num(lap.get('elevationLoss'), 0)

                        # -- Running Mechanics -------------------------------
                        cadence_avg  = f_num(lap.get('averageRunCadence'), 0)
                        cadence_max  = f_num(lap.get('maxRunCadence'), 0)
                        stride_raw   = lap.get('strideLength') or 0
                        stride_m     = stride_raw / 100 if stride_raw > 10 else stride_raw
                        gct_raw      = lap.get('groundContactTime') or 0  # ms
                        vert_osc     = f_num(lap.get('verticalOscillation'), 1)  # cm
                        vert_ratio   = f_num(lap.get('verticalRatio'), 1)        # %

                        # -- Power -------------------------------------------
                        avg_pwr      = lap.get('averagePower') or 0
                        max_pwr      = lap.get('maxPower') or 0
                        norm_pwr     = lap.get('normalizedPower') or 0
                        avg_wpkg     = avg_pwr / ATHLETE_WEIGHT_KG if avg_pwr else 0
                        max_wpkg     = max_pwr / ATHLETE_WEIGHT_KG if max_pwr else 0

                        # -- Environment -------------------------------------
                        calories     = f_num(lap.get('calories'), 0)
                        avg_temp     = f_num(lap.get('averageTemperature'), 1)

                        sep = "  |  "
                        print(f"\n    == Lap {lap_num} | {phase_label} ==")
                        print(f"       Distance:   {dist_km:.2f} km{sep}Moving Time: {fmt_time(moving_secs)}")
                        print(f"       Avg Pace:   {avg_pace} /km{sep}Mov Pace:    {moving_pace} /km")
                        print(f"       Best Pace:  {best_pace} /km{sep}GAP:         {gap_pace} /km")
                        print(f"       Avg HR:     {avg_hr} bpm{sep}Max HR:      {max_hr} bpm")
                        print(f"       Ascent:     +{elev_gain}m{sep}Descent:     -{elev_loss}m")
                        print(f"       Cadence:    {cadence_avg} spm{sep}Max Cadence: {cadence_max} spm")
                        print(f"       GCT:        {gct_raw:.0f} ms{sep}Stride:      {stride_m:.2f} m")
                        print(f"       Vert Osc:   {vert_osc} cm{sep}Vert Ratio:  {vert_ratio} %")
                        print(f"       Avg Power:  {avg_pwr:.0f} W{sep}NP:          {norm_pwr:.0f} W")
                        print(f"       Max Power:  {max_pwr:.0f} W{sep}Avg W/kg:    {avg_wpkg:.2f}  |  Max W/kg: {max_wpkg:.2f}")
                        print(f"       Calories:   {calories} kcal{sep}Avg Temp:    {avg_temp} C")

            except Exception as detail_err:
                print(f"    (Could not fetch split details: {detail_err})")

        # --- CYCLING ---
        rides = [a for a in activities if a['activityType']['typeKey'] == 'cycling']
        if rides:
            last_ride = rides[0]
            ride_id   = last_ride.get('activityId')
            speed_kmh = last_ride.get('averageSpeed', 0) * 3.6
            dur_min   = last_ride.get('duration', 0) / 60
            print(f"\n[ RIDE ] {last_ride.get('activityName')}")
            print(f"  - Date:     {last_ride.get('startTimeLocal', 'N/A')[:16]}")
            print(f"  - Distance: {last_ride.get('distance', 0) / 1000:.2f} km")
            print(f"  - Duration: {dur_min:.1f} mins")
            print(f"  - Avg Speed:{speed_kmh:.1f} km/h")
            print(f"  - Heart Rate: {f_num(last_ride.get('averageHR'), 0)} avg / {f_num(last_ride.get('maxHR'), 0)} max bpm")
            print(f"  - Elevation: +{f_num(last_ride.get('elevationGain'), 0)}m / -{f_num(last_ride.get('elevationLoss'), 0)}m")
            print(f"  - Temp (C): Avg {f_num(last_ride.get('avgTemperature'), 1)} | Max {f_num(last_ride.get('maxTemperature'), 1)}")
            print(f"  - Training Effect: Aerobic {f_num(last_ride.get('aerobicTrainingEffect'), 1)} | Anaerobic {f_num(last_ride.get('anaerobicTrainingEffect'), 1)}")
            print(f"  - Primary Benefit: {last_ride.get('trainingEffectLabel', 'N/A')}")
            try:
                ride_splits = client.get_activity_splits(ride_id)
                if ride_splits and 'lapDTOs' in ride_splits:
                    print("\n  [ Laps ]")
                    for lap in ride_splits['lapDTOs']:
                        lap_num  = lap.get('lapIndex')
                        lap_dist = lap.get('distance', 0) / 1000
                        lap_spd  = lap.get('averageSpeed', 0) * 3.6
                        lap_ahr  = f_num(lap.get('averageHR'), 0)
                        lap_mhr  = f_num(lap.get('maxHR'), 0)
                        print(f"    - Lap {lap_num}: {lap_dist:.2f} km | {lap_spd:.1f} km/h | HR: {lap_ahr}/{lap_mhr}")
            except Exception as ride_err:
                print(f"    (Could not fetch ride splits: {ride_err})")

        # --- STRENGTH ---
        strength = [a for a in activities if a['activityType']['typeKey'] == 'strength_training']
        for lift in strength[:2]:  # Show last 2 strength sessions
            lift_id = lift.get('activityId')
            lift_date = lift.get('startTimeLocal', 'N/A')[:16]
            print(f"\n[ LIFT ] {lift.get('activityName')} | {lift_date}")
            print(f"  - Duration: {lift.get('duration', 0) / 60:.1f} mins")
            print(f"  - Avg/Max HR: {f_num(lift.get('averageHR'), 0)} / {f_num(lift.get('maxHR'), 0)} bpm")

            # Fetch detailed exercise sets (exercises, reps, weight)
            try:
                ex_data = client.get_activity_exercise_sets(lift_id)
                ex_sets = ex_data.get("exerciseSets", [])
                active_sets = [s for s in ex_sets if s.get("setType") == "ACTIVE"]
                if active_sets:
                    print(f"  - Sets: {len(active_sets)} working sets")
                    # Group consecutive sets of the same exercise
                    current_exercise = None
                    set_group = []
                    for s in active_sets:
                        exercises = s.get("exercises", [])
                        if exercises:
                            ex_name = exercises[0].get("name") or None
                            ex_cat = exercises[0].get("category") or "?"
                        else:
                            ex_name = None
                            ex_cat = "?"
                        # Use category as display name when name is unavailable
                        if ex_name:
                            readable_name = str(ex_name).replace("_", " ").title()
                        else:
                            readable_name = str(ex_cat).replace("_", " ").title()
                        reps = s.get("repetitionCount", 0) or 0
                        weight_g = s.get("weight", 0) or 0
                        weight_kg = weight_g / 1000 if weight_g > 0 else 0
                        dur = s.get("duration", 0) or 0

                        if weight_kg > 0:
                            print(f"    - {readable_name} ({ex_cat}): "
                                  f"{reps} reps @ {weight_kg:.0f} kg | {dur:.0f}s")
                        elif reps > 0:
                            print(f"    - {readable_name} ({ex_cat}): "
                                  f"{reps} reps (BW) | {dur:.0f}s")
                        else:
                            print(f"    - {readable_name} ({ex_cat}): "
                                  f"{dur:.0f}s hold/timed")
            except Exception as ex_err:
                print(f"  (Could not fetch exercise details: {ex_err})")

        # -- KIAT ENGINE -------------------------------------------------------
        print("\n" + "="*55)
        print("  KIAT ENGINE -- PHYSIOLOGICAL METRICS")
        print("="*55)
        try:
            engine = PhysiologicalEngine()

            # Build sleep input
            eng_sleep = parse_sleep_data(sleep_dto)

            # Build HRV input
            eng_hrv_dict = {}
            if hrv_data and 'hrvSummary' in hrv_data:
                eng_hrv_dict = hrv_data['hrvSummary']
            eng_hrv = parse_hrv_data(eng_hrv_dict)

            # Build activity window (all 30d activities)
            eng_window = parse_activity_window(activities)

            # Extract last-run recovery hours and activity end time
            last_recovery_hours = None
            last_activity_end_utc = None
            if runs:
                last_run = runs[0]
                last_recovery_hours = last_run.get('recoveryTime') or None
                if last_recovery_hours:
                    last_recovery_hours = float(last_recovery_hours)
                start_raw = last_run.get('startTimeLocal') or ''
                duration_secs = last_run.get('duration') or 0
                if start_raw:
                    try:
                        dt_naive = datetime.fromisoformat(start_raw[:19].replace(' ', 'T'))
                        # Manila is UTC+8; subtract 8h to get UTC, then add duration
                        start_utc = dt_naive.replace(tzinfo=timezone.utc) - timedelta(hours=8)
                        last_activity_end_utc = start_utc + timedelta(seconds=duration_secs)
                    except ValueError:
                        pass

            # Rolling 3-day stress — use today's average as proxy
            stress_3d = summary.get('averageStressLevel')
            if stress_3d:
                stress_3d = float(stress_3d)

            # Extract lap kinematics from last run's splits (already fetched)
            eng_laps = []
            if runs:
                try:
                    act_id = runs[0].get('activityId')
                    lap_splits = client.get_activity_splits(act_id)
                    if lap_splits and 'lapDTOs' in lap_splits:
                        eng_laps = parse_laps(lap_splits['lapDTOs'])
                except Exception:
                    pass   # Lap data unavailable — REI/FBI will be N/A

            report = engine.compute(
                sleep=eng_sleep,
                hrv=eng_hrv,
                recovery_hours=last_recovery_hours,
                activity_end_time_utc=last_activity_end_utc,
                rolling_stress_3d=stress_3d,
                activity_window=eng_window,
                laps=eng_laps if eng_laps else None,
            )
            print(report.summary_text)

        except Exception as eng_err:
            print(f"[Physiological Engine Error] {eng_err}")

    except Exception as e:
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    run_sync()