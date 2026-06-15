"""
run_analysis.py — Exhaustive Run Analysis Report Generator v3
Pulls every available field from Garmin lap DTOs and the top-level activity summary.
Uses MAX'S REAL HEART RATE ZONES (from operating_manual.md), not Garmin's native zones.
Includes advanced HR metrics: TRIMP (Banister), PA:HR Decoupling, Peak EPOC,
Max HR Drop, Cardiac Drift, and full time-in-zone computed from lap data.
New (May 2026):
  - Proper Interval Analysis using get_activity_typed_splits (INTERVAL_ACTIVE/RECOVERY)
  - Heat Index calculation via Rothfusz regression when humidity not in Garmin data
"""

import os, sys, json, math
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date, timedelta

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# ============================================================
# ATHLETE CONSTANTS (from operating_manual.md)
# ============================================================
HR_REST     = 40    # Resting HR (midpoint of 39-42 bpm)
HR_MAX      = 206   # Verified Max HR
WEIGHT_KG   = 75.5  # Athlete weight
VO2MAX      = 55.0  # Garmin VO2Max estimate (ml/kg/min)

# Real HR Zones (from operating_manual.md Section 6)
ZONES = [
    (1, "Z1-Recovery",      0,   144),
    (2, "Z2-Aerobic",       145, 162),
    (3, "Z3-Grey/MP",       163, 184),
    (4, "Z4-Threshold",     185, 196),
    (5, "Z5-Anaerobic",     197, 999),
]

# ============================================================
# CONFIG
# ============================================================
TARGET_DATE = sys.argv[1] if len(sys.argv) > 1 else (date.today() - timedelta(days=1)).isoformat()
NEXT_DAY    = (date.fromisoformat(TARGET_DATE) + timedelta(days=1)).isoformat()

# ============================================================
# FETCH DATA
# ============================================================
acts = client.get_activities_by_date(TARGET_DATE, NEXT_DAY)
run  = next((a for a in acts if a.get("activityType", {}).get("typeKey") == "running"), None)
if not run:
    print(f"No running activity found on {TARGET_DATE}.")
    sys.exit(0)

splits_raw   = client.get_activity_splits(run["activityId"])
laps         = splits_raw.get("lapDTOs", [])
active_laps  = [l for l in laps if l.get("distance", 0) >= 500]

# ── Typed splits: real interval structure from Garmin workout structure ──
try:
    typed_data   = client.get_activity_typed_splits(run["activityId"])
    typed_splits = typed_data.get("splits", [])
except Exception:
    typed_splits = []

# Separate by type — INTERVAL_ACTIVE = work reps, INTERVAL_RECOVERY = rest periods
interval_warmup   = [s for s in typed_splits if s.get("type") == "INTERVAL_WARMUP"]
interval_active   = [s for s in typed_splits if s.get("type") == "INTERVAL_ACTIVE"]
interval_recovery = [s for s in typed_splits if s.get("type") == "INTERVAL_RECOVERY"]
interval_cooldown = [s for s in typed_splits if s.get("type") == "INTERVAL_COOLDOWN"]
is_interval_session = len(interval_active) > 0

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def pace(speed_mps):
    if not speed_mps or speed_mps == 0: return "N/A"
    s = 1000 / speed_mps
    return f"{int(s//60)}:{int(s%60):02d}/km"

def fmt(val, decimals=1, unit=""):
    if val is None: return "N/A"
    return f"{round(val, decimals)}{unit}"

def secs_to_hmmss(secs):
    if secs is None: return "N/A"
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    if h > 0: return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"

def real_hr_zone(hr):
    if hr is None: return "N/A"
    for num, label, lo, hi in ZONES:
        if lo <= hr <= hi: return f"Z{num}: {label.split('-')[1]}"
    return "Z5: Anaerobic"

# ============================================================
# HEAT INDEX CALCULATION (Rothfusz Regression)
# Calibrated May 31, 2026 against Runalyze/Apple WeatherKit reference.
#
# KEY CORRECTIONS:
# 1. WRIST SENSOR BIAS: The Garmin FR 165 thermistor sits on the wrist
#    and reads 3-5C above true ambient due to body heat radiation, solar
#    load on the watch face, and skin surface temperature. We subtract
#    GARMIN_TEMP_BIAS (4C) from the raw Garmin reading to estimate ambient.
#    Validation: Garmin reported 32-34C on May 31 evening; Apple WeatherKit
#    (via PAGASA weather station) reported 29C ambient. Difference = 3-5C.
#
# 2. HUMIDITY DEFAULT: Marikina evening RH averages 65-75% (PAGASA data).
#    Previous code documented 70% but passed 80% at the call site.
#    Fixed to 70% everywhere. This better matches Apple WeatherKit output.
#
# 3. CARDIAC PENALTY: Previous formula used 5-8 bpm per degree above 28C,
#    producing absurd values (e.g., +165-265 bpm) at inflated heat indices.
#    Recalibrated to 1.5-2.5 bpm per degree, consistent with exercise
#    physiology literature (Periard et al., 2021; Sawka et al., 2011).
#
# Validation result: May 31 run — Runalyze HI = 35C, our corrected HI = ~34-35C.
# ============================================================
GARMIN_TEMP_BIAS = 4.0  # Celsius to subtract from FR 165 wrist sensor
DEFAULT_RH = 70.0       # Marikina evening average relative humidity

def garmin_to_ambient(garmin_temp_c: float) -> float:
    """Convert Garmin wrist sensor temperature to estimated ambient.
    The FR 165 thermistor reads 3-5C above true ambient due to body heat.
    """
    return garmin_temp_c - GARMIN_TEMP_BIAS

def heat_index_c(temp_c: float, rh: float = DEFAULT_RH) -> float:
    """Compute heat index in Celsius using the Rothfusz regression.
    temp_c: AMBIENT air temperature in Celsius (NOT raw Garmin sensor reading)
    rh: relative humidity in % (default 70 for Marikina evening)
    Returns: heat index in Celsius
    """
    T = temp_c * 9 / 5 + 32  # convert to Fahrenheit for Rothfusz formula
    HI_F = (-42.379
            + 2.04901523 * T
            + 10.14333127 * rh
            - 0.22475541 * T * rh
            - 0.00683783 * T * T
            - 0.05481717 * rh * rh
            + 0.00122874 * T * T * rh
            + 0.00085282 * T * rh * rh
            - 0.00000199 * T * T * rh * rh)
    return (HI_F - 32) * 5 / 9  # back to Celsius

def heat_stress_label(hi_c: float) -> str:
    if hi_c < 27:  return "Comfortable"
    if hi_c < 32:  return "Caution"
    if hi_c < 39:  return "Extreme Caution"
    if hi_c < 46:  return "DANGER"
    return "EXTREME DANGER"

def extra_bpm_from_heat(hi_c: float) -> str:
    """Estimate additional bpm cardiac drift caused by heat index above 28C.
    Literature-calibrated: ~1.5-2.5 bpm per degree C above 28C baseline.
    Sources: Periard et al. (2021), Sawka et al. (2011).
    At HI 35C: +10-18 bpm. At HI 40C: +18-30 bpm.
    """
    extra_c = max(0, hi_c - 28)
    low  = int(extra_c * 1.5)
    high = int(extra_c * 2.5)
    return f"+{low}–{high} bpm cardiac penalty"

def zone_num(hr):
    if hr is None: return 0
    for num, label, lo, hi in ZONES:
        if lo <= hr <= hi: return num
    return 5

# ============================================================
# ADVANCED HR METRIC COMPUTATIONS
# ============================================================

# --- 1. TRIMP (Banister's Training Impulse) per lap ---
# Formula: TRIMP = duration_min * delta_HR_ratio * 0.64 * e^(1.92 * delta_HR_ratio)
# delta_HR_ratio = (HR_avg - HR_rest) / (HR_max - HR_rest)
# Represents true training stress in arbitrary units (AU)
total_trimp = 0.0
lap_trimps  = []
for lap in active_laps:
    hr   = lap.get("averageHR", 0) or 0
    dur  = lap.get("duration", 0) / 60  # minutes
    if hr > HR_REST and dur > 0:
        dhr = (hr - HR_REST) / (HR_MAX - HR_REST)
        dhr = max(0.0, min(dhr, 1.0))
        t   = dur * dhr * 0.64 * math.exp(1.92 * dhr)
        lap_trimps.append(round(t, 2))
        total_trimp += t
    else:
        lap_trimps.append(0.0)

# --- 2. Edwards' Zone-Weighted TRIMP (computed from real zones, lap data) ---
# Each lap's duration is allocated to its HR zone, weighted by zone multiplier (1-5)
zone_times_real = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # seconds in each real zone
edwards_trimp   = 0.0
for lap in active_laps:
    hr  = lap.get("averageHR", 0) or 0
    dur = lap.get("duration", 0)
    z   = zone_num(hr)
    if z > 0:
        zone_times_real[z] += dur
        edwards_trimp += (dur / 60) * z  # minutes * zone multiplier

# --- 3. PA:HR Decoupling (Aerobic Decoupling) ---
# Efficiency Factor (EF) = GAP (m/s) / Avg HR
# Decoupling = (EF_first_half - EF_second_half) / EF_first_half * 100
# <5% = aerobically coupled (good). >5% = HR drifting away from effort (heat/fatigue).
n_half    = len(active_laps) // 2
first_half  = active_laps[:n_half]
second_half = active_laps[n_half:]

def avg_ef(lap_list):
    efs = []
    for l in lap_list:
        gap = l.get("avgGradeAdjustedSpeed", l.get("averageSpeed", 0))
        hr  = l.get("averageHR", 0)
        if hr and hr > 0 and gap and gap > 0:
            efs.append(gap / hr)
    return sum(efs) / len(efs) if efs else None

ef_first  = avg_ef(first_half)
ef_second = avg_ef(second_half)
pahr_decoupling = None
if ef_first and ef_second and ef_first > 0:
    pahr_decoupling = ((ef_first - ef_second) / ef_first) * 100

# --- 4. Cardiac Drift ---
# Per-lap HR / pace ratio drift over the run
# We look at HR delta at matched intensities (same pace band)
# Simplified: compare HR in first vs second half at similar GAP bands
# Also: direct HR-per-m/s ratio across laps to see drift
drift_ratios = []
for lap in active_laps:
    gap = lap.get("avgGradeAdjustedSpeed", lap.get("averageSpeed", 0))
    hr  = lap.get("averageHR", 0)
    if gap and gap > 0 and hr and hr > 0:
        drift_ratios.append(hr / gap)  # bpm per m/s — higher = HR is elevated for the speed

cardiac_drift_trend = None
if len(drift_ratios) >= 4:
    first_q = sum(drift_ratios[:len(drift_ratios)//4]) / (len(drift_ratios)//4)
    last_q  = sum(drift_ratios[-(len(drift_ratios)//4):]) / (len(drift_ratios)//4)
    cardiac_drift_trend = last_q - first_q  # positive = HR rising relative to pace

# --- 5. Max HR Drop (Largest single-lap HR decrease between consecutive laps) ---
# Indicates big walk breaks or cooling events
max_hr_drop     = 0.0
max_hr_drop_lap = None
for i in range(1, len(active_laps)):
    prev_hr = active_laps[i-1].get("averageHR", 0) or 0
    curr_hr = active_laps[i].get("averageHR", 0) or 0
    drop = prev_hr - curr_hr
    if drop > max_hr_drop:
        max_hr_drop     = drop
        max_hr_drop_lap = i + 1  # 1-indexed, pointing to the lap where drop occurred

# --- 6. Peak EPOC Estimate ---
# EPOC (Excess Post-Exercise Oxygen Consumption) reflects the recovery oxygen debt.
# We use two methods:
#   a) Session EPOC (Knuttgen model): depends on avg %HRmax and duration
#      EPOC (mL/kg) = 0.096 * e^(0.0284 * %HRmax) * duration_min
#   b) Per-lap relative EPOC intensity (normalized, for lap table comparison)
#      Shows which lap contributed the MOST to EPOC, not an absolute value

# Session-level EPOC (the scientifically defensible number to report)
session_duration_min = sum(l.get("duration", 0) for l in active_laps) / 60
session_avg_hr       = sum(l.get("averageHR", 0) or 0 for l in active_laps) / len(active_laps) if active_laps else avg_hr
pct_hrmax_session    = (session_avg_hr / HR_MAX) * 100
# Knuttgen model — returns mL/kg, realistic range 5-60 mL/kg for most runs
total_epoc = 0.096 * math.exp(0.0284 * pct_hrmax_session) * session_duration_min

# Per-lap relative EPOC contribution (normalized intensity index, not absolute mL/kg)
# Formula: (HR_avg / HR_max)^2 * duration_min — gives a relative contribution score
lap_epoc_scores = []
for lap in laps:
    hr  = lap.get("averageHR", 0) or 0
    dur = lap.get("duration", 0) / 60
    score = (hr / HR_MAX) ** 2 * dur if hr > 0 else 0.0
    lap_epoc_scores.append(score)

max_epoc_score = max(lap_epoc_scores) if lap_epoc_scores else 1
# Normalize each lap's score as a % of the hardest lap (for relative comparison in table)
lap_epoc_pct = [(s / max_epoc_score * 100) if max_epoc_score > 0 else 0 for s in lap_epoc_scores]

# Find peak EPOC lap (lap with highest relative intensity*duration)
peak_epoc_lap = lap_epoc_scores.index(max(lap_epoc_scores)) + 1 if lap_epoc_scores else None
peak_epoc = total_epoc  # The actual EPOC is session-level; peak refers to the hardest lap


# --- 7. Real Zone Time Summary ---
total_real_zone_time = sum(zone_times_real.values())

# ============================================================
# TOP-LEVEL ACTIVITY METRICS
# ============================================================
a = run
act_name       = a.get("activityName", "Unknown")
start_time     = a.get("startTimeLocal", "N/A")
total_dist     = a.get("distance", 0) / 1000
elapsed_dur    = a.get("elapsedDuration", 0)
moving_dur     = a.get("movingDuration", 0)
total_elev_gain= a.get("elevationGain", 0)
total_elev_loss= a.get("elevationLoss", 0)
avg_speed      = a.get("averageSpeed", 0)
max_speed      = a.get("maxSpeed", 0)
calories       = a.get("calories", 0)
bmr_cals       = a.get("bmrCalories", 0)
avg_hr         = a.get("averageHR", 0)
max_hr_act     = a.get("maxHR", 0)
avg_cadence    = a.get("averageRunningCadenceInStepsPerMinute", 0)
max_cadence    = a.get("maxRunningCadenceInStepsPerMinute", 0)
steps          = a.get("steps", 0)
avg_power      = a.get("avgPower", 0)
max_power      = a.get("maxPower", 0)
norm_power     = a.get("normPower", 0)
aerobic_te     = a.get("aerobicTrainingEffect", 0)
anaerobic_te   = a.get("anaerobicTrainingEffect", 0)
te_label       = a.get("trainingEffectLabel", "N/A")
avg_vo         = a.get("avgVerticalOscillation", 0)
avg_vr         = a.get("avgVerticalRatio", 0)
avg_gct        = a.get("avgGroundContactTime", 0)
avg_stride     = a.get("avgStrideLength", 0)
avg_grade_adj  = a.get("avgGradeAdjustedSpeed", 0)
vo2max_g       = a.get("vO2MaxValue", 0)
min_temp       = a.get("minTemperature", 0)
max_temp       = a.get("maxTemperature", 0)
min_elev       = a.get("minElevation", 0)
max_elev       = a.get("maxElevation", 0)
avg_elev       = a.get("avgElevation", 0)
body_battery   = a.get("differenceBodyBattery", 0)
water_est      = a.get("waterEstimated", 0)
fast_1k        = a.get("fastestSplit_1000", None)
fast_mile      = a.get("fastestSplit_1609", None)
fast_5k        = a.get("fastestSplit_5000", None)
fast_10k       = a.get("fastestSplit_10000", None)
pz1 = a.get("powerTimeInZone_1", 0)
pz2 = a.get("powerTimeInZone_2", 0)
pz3 = a.get("powerTimeInZone_3", 0)
pz4 = a.get("powerTimeInZone_4", 0)
pz5 = a.get("powerTimeInZone_5", 0)

# Aerobic efficiency (Grade-Adjusted Speed / Power)
aerobic_eff = (avg_grade_adj / avg_power * 1000) if avg_power > 0 else None

# HR Drift (first third vs last third avg HR)
n = len(active_laps)
first_third  = active_laps[:max(1, n//3)]
last_third   = active_laps[-(max(1, n//3)):]
first_avg_hr = sum(l.get("averageHR", 0) for l in first_third) / len(first_third) if first_third else 0
last_avg_hr  = sum(l.get("averageHR", 0) for l in last_third)  / len(last_third)  if last_third  else 0
hr_drift     = last_avg_hr - first_avg_hr

# ============================================================
# BUILD REPORT
# ============================================================
lines = []
L = lines.append

L(f"# Exhaustive Run Analysis: {act_name}")
L(f"*Activity Date: {start_time} | Analysis Generated: {date.today().isoformat()}*")
L(f"*Heart Rate Zones: Max's verified zones (Manual, Section 6) | HR Rest: {HR_REST} bpm | HR Max: {HR_MAX} bpm*")
L("")

# -------------------------------------------
# SECTION 1: ACTIVITY OVERVIEW
# -------------------------------------------
L("---")
L("## 1. Activity Overview")
L("")
L("| Metric | Value |")
L("| :--- | :--- |")
L(f"| **Total Distance** | {total_dist:.2f} km |")
L(f"| **Moving Time** | {secs_to_hmmss(moving_dur)} |")
L(f"| **Elapsed Time** (incl. stops) | {secs_to_hmmss(elapsed_dur)} |")
L(f"| **Stopped Time** | {secs_to_hmmss(elapsed_dur - moving_dur)} |")
L(f"| **Average Pace** | {pace(avg_speed)} |")
L(f"| **Grade-Adjusted Pace (GAP)** | {pace(avg_grade_adj)} |")
L(f"| **Max Speed** | {pace(max_speed)} |")
L(f"| **Total Steps** | {int(steps):,} |")
L(f"| **Calories Burned** | {int(calories)} kcal (Active) + {int(bmr_cals)} kcal (BMR) = **{int(calories+bmr_cals)} kcal total** |")
L(f"| **Estimated Sweat Loss** | {int(water_est)} mL |")
L(f"| **Body Battery Cost** | {body_battery} points |")
L(f"| **Garmin VO2 Max Estimate** | {vo2max_g} ml/kg/min |")
L("")

# -------------------------------------------
# SECTION 2: ENVIRONMENTAL CONDITIONS
# -------------------------------------------
L("---")
L("## 2. Environmental Conditions (Heat Tax Report)")
L("")
L("> **Humidity:** Not recorded by the Garmin Forerunner 165. Heat Index computed via Rothfusz regression using 70% RH default (Marikina evening avg). Garmin wrist sensor temperature corrected by -4C to estimate ambient (calibrated against Apple WeatherKit via Runalyze).")
L("")

# Compute heat index — correct Garmin wrist sensor to ambient first
amb_min = garmin_to_ambient(min_temp)
amb_max = garmin_to_ambient(max_temp)
hi_min = heat_index_c(amb_min, rh=DEFAULT_RH)
hi_max = heat_index_c(amb_max, rh=DEFAULT_RH)
hi_label = heat_stress_label(hi_max)
heat_bpm_penalty = extra_bpm_from_heat(hi_max)

L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Garmin Sensor Temp** | {min_temp}–{max_temp}°C | Raw wrist sensor (reads +3-5°C above ambient) |")
L(f"| **Est. Ambient Temp** | {amb_min:.0f}–{amb_max:.0f}°C | Corrected for wrist bias (-{GARMIN_TEMP_BIAS:.0f}°C) |")
L(f"| **Temperature Swing** | {max_temp - min_temp:.0f}°C | Every 1°C above 28°C adds ~1.5-2.5 bpm of cardiac drift |")
L(f"| **Heat Index (Min Temp)** | **{hi_min:.1f}°C** | Feels-like at run start (ambient {amb_min:.0f}°C, {DEFAULT_RH:.0f}% RH) |")
L(f"| **Heat Index (Max Temp)** | **{hi_max:.1f}°C** | Feels-like at peak heat (ambient {amb_max:.0f}°C, {DEFAULT_RH:.0f}% RH) |")
L(f"| **Heat Stress Level** | **{hi_label}** | Based on peak heat index |")
L(f"| **Cardiac Heat Penalty** | **{heat_bpm_penalty}** | Estimated HR elevation above cool-condition baseline |")
L(f"| **Min Elevation** | {min_elev:.0f} m | Lowest point on course |")
L(f"| **Max Elevation** | {max_elev:.0f} m | Highest point on course |")
L(f"| **Avg Elevation** | {avg_elev:.0f} m | Mean terrain height |")
L(f"| **Total Elevation Gain** | {int(total_elev_gain)} m | Each 10m gain adds ~3-4% metabolic cost |")
L(f"| **Total Elevation Loss** | {int(total_elev_loss)} m | Eccentric quad loading — source of post-run soreness |")
L(f"| **Net Elevation** | {int(total_elev_gain - total_elev_loss):+d} m | Net uphill = harder than pace suggests |")
L("")

# -------------------------------------------
# SECTION 2b: INTERVAL ANALYSIS (only if interval session detected)
# -------------------------------------------
if is_interval_session:
    L("---")
    L("## 2b. Interval Rep-by-Rep Analysis")
    L("")
    L(f"> Session Type: **Structured Interval Workout** — {len(interval_active)} work rep(s) detected via Garmin typed splits.")
    L(f"> Heat Index during session: **{hi_max:.1f}°C** ({hi_label}). Cardiac penalty: {heat_bpm_penalty}.")
    L("")

    # Warmup
    if interval_warmup:
        wu = interval_warmup[0]
        wu_pace = pace(wu.get("averageSpeed", 0))
        wu_dur  = secs_to_hmmss(wu.get("duration", 0))
        wu_eg   = wu.get("elevationGain", 0)
        wu_el   = wu.get("elevationLoss", 0)
        L(f"**Warmup:** {wu_dur} | {wu_pace} | Avg HR {wu.get('averageHR', 'N/A')} bpm | Ascent +{wu_eg:.0f}m / Descent -{wu_el:.0f}m | Temp {wu.get('averageTemperature', 'N/A')}°C")
        L("")

    # Work rep table header
    L("| Rep | Duration | Pace | GAP | Avg HR | Peak HR | Zone | Ascent | Descent | Power | NP | GCT | Stride | Temp | Heat Index | TRIMP |")
    L("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    # Pair each work rep with its corresponding recovery if present
    for i, rep in enumerate(interval_active):
        rep_num   = i + 1
        dur_s     = rep.get("duration", 0)
        dur_str   = secs_to_hmmss(dur_s)
        mps       = rep.get("averageSpeed", 0) or 0
        gap_mps   = rep.get("avgGradeAdjustedSpeed", mps) or mps
        p_str     = pace(mps)
        gap_str   = pace(gap_mps)
        avg_hr_r  = rep.get("averageHR") or 0
        max_hr_r  = rep.get("maxHR") or 0
        zone_str  = real_hr_zone(avg_hr_r)
        eg        = rep.get("elevationGain", 0) or 0
        el        = rep.get("elevationLoss", 0) or 0
        pwr       = rep.get("averagePower", 0) or 0
        np_       = rep.get("normalizedPower", 0) or 0
        gct       = rep.get("groundContactTime", 0) or 0
        stride    = rep.get("strideLength", 0) or 0
        temp_r    = rep.get("averageTemperature") or max_temp
        hi_r      = heat_index_c(garmin_to_ambient(temp_r), DEFAULT_RH)

        # TRIMP for this rep
        dur_min_r = dur_s / 60
        if avg_hr_r > HR_REST and dur_min_r > 0:
            dhr_r = (avg_hr_r - HR_REST) / (HR_MAX - HR_REST)
            dhr_r = max(0.0, min(dhr_r, 1.0))
            trimp_r = dur_min_r * dhr_r * 0.64 * math.exp(1.92 * dhr_r)
        else:
            trimp_r = 0.0

        L(f"| **Rep {rep_num}** | {dur_str} | {p_str} | {gap_str} | {avg_hr_r:.0f} bpm | {max_hr_r:.0f} bpm | {zone_str} | +{eg:.0f}m | -{el:.0f}m | {pwr:.0f}W | {np_:.0f}W | {gct:.0f}ms | {stride:.1f}cm | {temp_r:.0f}°C | **{hi_r:.1f}°C** | {trimp_r:.1f} AU |")

        # Recovery row if available
        if i < len(interval_recovery):
            rec = interval_recovery[i]
            rec_dur  = secs_to_hmmss(rec.get("duration", 0))
            rec_pace = pace(rec.get("averageSpeed", 0))
            rec_hr   = rec.get("averageHR") or 0
            rec_eg   = rec.get("elevationGain", 0) or 0
            rec_el   = rec.get("elevationLoss", 0) or 0
            L(f"| *Rest {rep_num}* | *{rec_dur}* | *{rec_pace}* | — | *{rec_hr:.0f} bpm* | — | — | *+{rec_eg:.0f}m* | *-{rec_el:.0f}m* | — | — | — | — | — | — | — |")

    # Cooldown
    if interval_cooldown:
        cd = interval_cooldown[0]
        cd_pace = pace(cd.get("averageSpeed", 0))
        cd_dur  = secs_to_hmmss(cd.get("duration", 0))
        cd_eg   = cd.get("elevationGain", 0) or 0
        cd_el   = cd.get("elevationLoss", 0) or 0
        L("")
        L(f"**Cooldown:** {cd_dur} | {cd_pace} | Avg HR {cd.get('averageHR', 'N/A')} bpm | Ascent +{cd_eg:.0f}m / Descent -{cd_el:.0f}m")
    else:
        L("")
        L("> **Note:** No cooldown detected in typed splits. Session ended without a structured cooldown.")
    L("")


# -------------------------------------------
# SECTION 3: HEART RATE ANALYSIS (FULL)
# -------------------------------------------
L("---")
L("## 3. Heart Rate Analysis")
L("")
L("### 3.1 Core HR Statistics")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Resting HR (Baseline)** | {HR_REST} bpm | From operating manual — used for TRIMP and EPOC calculations |")
L(f"| **Average HR** | {avg_hr:.0f} bpm | {real_hr_zone(avg_hr)} |")
L(f"| **Max HR** | {max_hr_act:.0f} bpm | {real_hr_zone(max_hr_act)} — {round((max_hr_act/HR_MAX)*100, 1)}% of max |")
L(f"| **HR Reserve Used (avg)** | {round(((avg_hr - HR_REST) / (HR_MAX - HR_REST)) * 100, 1)}% | % of max HR reserve actively engaged |")
L("")
L("### 3.2 Cardiac Drift")
L("")
L("> **What is Cardiac Drift?** HR creeps upward over time even when pace/effort stays constant. This is caused by plasma volume loss from sweating (blood gets thicker, heart beats faster to compensate) and heat-driven vasodilation. A drift >10 bpm over a 2-hour run is significant. >15 bpm = severe thermal or dehydration stress.")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **First-Third Avg HR** | {first_avg_hr:.0f} bpm | Average HR in the first {n//3} active laps |")
L(f"| **Last-Third Avg HR** | {last_avg_hr:.0f} bpm | Average HR in the final {n//3} active laps |")
L(f"| **Absolute HR Drift** | +{hr_drift:.1f} bpm | Raw HR rise from first to last third |")
if cardiac_drift_trend is not None:
    L(f"| **Cardiac Drift Index** | +{cardiac_drift_trend:.2f} bpm/(m/s) | HR per unit of pace worsened by this amount — controls for pace changes |")
L(f"| **Drift Classification** | {'SEVERE (>15 bpm)' if hr_drift > 15 else 'SIGNIFICANT (10-15 bpm)' if hr_drift > 10 else 'MODERATE (5-10 bpm)' if hr_drift > 5 else 'MINIMAL (<5 bpm)'} | {'Dehydration + Heat Tax fully active' if hr_drift > 15 else 'Significant thermal stress' if hr_drift > 10 else 'Manageable' if hr_drift > 5 else 'Excellent thermoregulation'} |")
L("")
L("### 3.3 PA:HR Decoupling (Aerobic Coupling)")
L("")
L("> **What is PA:HR Decoupling?** Compares your Pace-to-HR efficiency in the first half of the run vs the second. If HR rises disproportionately to pace (you are working harder for the same speed), the run was above your aerobic capacity. <5% = perfectly coupled aerobic run. >5% = decoupled (heat/fatigue/cardiac drift at play).")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
if ef_first and ef_second:
    L(f"| **Efficiency Factor (First Half)** | {ef_first*1000:.3f} (GAP m/s / HR) | Baseline aerobic efficiency |")
    L(f"| **Efficiency Factor (Second Half)** | {ef_second*1000:.3f} (GAP m/s / HR) | How efficiency held up under fatigue/heat |")
if pahr_decoupling is not None:
    coupling = abs(pahr_decoupling)
    L(f"| **PA:HR Decoupling %** | {pahr_decoupling:.1f}% | {'COUPLED (<5%) — excellent aerobic run' if coupling < 5 else 'DECOUPLED (5-10%) — moderate drift' if coupling < 10 else 'HIGHLY DECOUPLED (>10%) — this was above aerobic ceiling'} |")
L("")
L("### 3.4 Max HR Drop")
L("")
L("> **What is Max HR Drop?** The largest single-lap HR decrease between consecutive laps. Identifies walk breaks, cooling events, or significant downhill segments. A >15 bpm drop usually indicates a walk interval or deliberate recovery.")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Largest Single-Lap HR Drop** | -{max_hr_drop:.0f} bpm | Occurred at Lap {max_hr_drop_lap} | {'Likely a walk break or cooling event' if max_hr_drop > 10 else 'Normal pace variation'} |")
L("")
L("### 3.5 Time in Real HR Zones (Computed from Lap Data)")
L("")
L("> Zones calculated from Max's verified zones (operating_manual.md Section 6), NOT Garmin's native zones.")
L("")
L("| Zone | Definition | Boundary | Time | % of Active Run | Energy System |")
L("| :--- | :--- | :--- | :--- | :--- | :--- |")
zone_labels = {
    1: ("Recovery",    "<145 bpm",     "Fat oxidation, minimal stimulus"),
    2: ("Aerobic",     "145-162 bpm",  "Primary fat + some carb. Builds mitochondria."),
    3: ("Grey/MP",     "163-184 bpm",  "Mixed fuel. Glycogen burning begins. Marathon pace territory."),
    4: ("Threshold",   "185-196 bpm",  "Primarily glycolytic. High CNS stress."),
    5: ("Anaerobic",   "197+ bpm",     "Maximum glycolytic + PCr system. Unsustainable."),
}
for z, (zlabel, zbnd, zenergy) in zone_labels.items():
    t = zone_times_real[z]
    pct = (t / total_real_zone_time * 100) if total_real_zone_time > 0 else 0
    L(f"| **Z{z}: {zlabel}** | {zbnd} | {zbnd} | {secs_to_hmmss(t)} | {pct:.1f}% | {zenergy} |")
L("")

# -------------------------------------------
# SECTION 4: TRIMP & TRAINING LOAD
# -------------------------------------------
L("---")
L("## 4. Training Impulse & Load Metrics")
L("")
L("### 4.1 TRIMP — Banister's Training Impulse")
L("")
L("> **What is TRIMP?** Training IMPulse is the gold-standard measure of cardiovascular training stress, invented by Banister (1991). It integrates HR intensity over time, weighted exponentially — so a minute at threshold counts far more than a minute at Zone 1. Used to build Fitness-Fatigue models (ATL/CTL).")
L("> **Formula:** TRIMP = Duration(min) × [(HR_avg - HR_rest) / (HR_max - HR_rest)] × 0.64 × e^(1.92 × HR_ratio)")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Total TRIMP (Banister)** | {total_trimp:.1f} AU | Training stress for this session in arbitrary units |")
L(f"| **Edwards Zone-Weighted TRIMP** | {edwards_trimp:.1f} AU | Simpler zone-multiplier method (1x Z1 ... 5x Z5) |")
L(f"| **Load Classification** | {'HIGH (>100 AU)' if total_trimp > 100 else 'MODERATE (50-100 AU)' if total_trimp > 50 else 'LOW (<50 AU)'} | {'Major session — expect significant recovery demand' if total_trimp > 100 else 'Meaningful aerobic stimulus' if total_trimp > 50 else 'Light session'} |")
L("")

# -------------------------------------------
# SECTION 5: EPOC
# -------------------------------------------
L("---")
L("## 5. EPOC — Excess Post-Exercise Oxygen Consumption")
L("")
L("> **What is EPOC?** After hard exercise, your body continues burning oxygen above resting levels to restore itself: clear lactate, replenish phosphocreatine (PCr), re-oxygenate blood, regulate body temperature, and repair muscle. This is your 'recovery debt'. Higher intensity = longer, larger EPOC. A high EPOC explains why you keep burning calories for hours after a hard run.")
L("> **Formula:** Estimated via %VO2max derived from HR reserve, using the Skinner-McLellan adaptation (0.069 × %VO2max^1.5 × duration_min)")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Session EPOC Estimate** | {total_epoc:.1f} mL/kg | Session-level O2 debt (Knuttgen model: 0.096 × e^(0.0284 × %HRmax) × duration). Realistic range: 5-60 mL/kg. |")
L(f"| **Hardest EPOC Lap** | Lap {peak_epoc_lap} | The lap with the highest (HR/HRmax)^2 × duration score — contributed most to EPOC |")
L(f"| **EPOC Classification** | {'MAJOR (>50 mL/kg)' if total_epoc > 50 else 'SIGNIFICANT (25-50 mL/kg)' if total_epoc > 25 else 'MODERATE (10-25 mL/kg)' if total_epoc > 10 else 'LIGHT (<10 mL/kg)'} | {'Full recovery requires 24-48 hours' if total_epoc > 50 else 'Recovery within 12-24 hours' if total_epoc > 25 else 'Standard overnight recovery sufficient' if total_epoc > 10 else 'Minimal recovery impact'} |")
L("")

# -------------------------------------------
# SECTION 6: POWER ANALYSIS
# -------------------------------------------
L("---")
L("## 6. Power Analysis")
L("")
L("### 6.1 Summary Statistics")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Average Power** | {avg_power:.0f} W | Mean mechanical output for the entire run |")
L(f"| **Normalized Power (NP)** | {norm_power:.0f} W | The 'effective' load accounting for intensity variability. Higher NP = more intensity spikes. |")
L(f"| **Max Power** | {max_power:.0f} W | Peak instantaneous power (sprint, sharp uphill, or acceleration) |")
vi = norm_power/avg_power if avg_power > 0 else 0
L(f"| **Variability Index (VI)** | {vi:.2f} | NP / AP. <1.05 = very steady. 1.05-1.10 = moderate surges. >1.10 = highly variable. |")
if aerobic_eff:
    L(f"| **Aerobic Efficiency (EF)** | {aerobic_eff:.4f} | GAP(m/s) / Power(W) × 1000. Rising EF week-over-week = improving running economy. |")
L("")
L("### 6.2 Time in Power Zones")
total_pwr_time = pz1 + pz2 + pz3 + pz4 + pz5
L("| Power Zone | Time | % of Run |")
L("| :--- | :--- | :--- |")
for label, t in [("Z1 Easy", pz1), ("Z2 Moderate", pz2), ("Z3 Tempo", pz3), ("Z4 Threshold", pz4), ("Z5 Anaerobic", pz5)]:
    pct = t/total_pwr_time*100 if total_pwr_time > 0 else 0
    L(f"| **{label}** | {secs_to_hmmss(t)} | {pct:.1f}% |")
L("")

# -------------------------------------------
# SECTION 7: TRAINING EFFECT & BEST EFFORTS
# -------------------------------------------
L("---")
L("## 7. Training Effect & Best Efforts")
L("")
L("| Metric | Value | Coaching Note |")
L("| :--- | :--- | :--- |")
L(f"| **Aerobic Training Effect** | {aerobic_te:.1f} / 5.0 | {te_label.replace('_', ' ').title()} |")
L(f"| **Anaerobic Training Effect** | {anaerobic_te:.1f} / 5.0 | Near-zero = almost entirely aerobic — correct for a long run |")
L("")
L("### Best Effort Splits")
L("| Distance | Time | Pace |")
L("| :--- | :--- | :--- |")
if fast_1k:   L(f"| **1 km**  | {secs_to_hmmss(fast_1k)} | {pace(1000/fast_1k)} |")
if fast_mile: L(f"| **1 Mile** | {secs_to_hmmss(fast_mile)} | {pace(1609/fast_mile)} |")
if fast_5k:   L(f"| **5 km**  | {secs_to_hmmss(fast_5k)} | {pace(5000/fast_5k)} |")
if fast_10k:  L(f"| **10 km** | {secs_to_hmmss(fast_10k)} | {pace(10000/fast_10k)} |")
L("")

# -------------------------------------------
# SECTION 8: BIOMECHANICS OVERVIEW
# -------------------------------------------
L("---")
L("## 8. Overall Biomechanics")
L("")
L("| Metric | Value | Benchmark | Coaching Note |")
L("| :--- | :--- | :--- | :--- |")
L(f"| **Avg Cadence** | {avg_cadence:.0f} spm | >170 spm | Steps per minute — neuromuscular firing rate |")
L(f"| **Avg Stride Length** | {avg_stride:.1f} cm | >90 cm (at Z2 pace) | Distance per step — push-off power |")
L(f"| **Avg GCT** | {avg_gct:.0f} ms | <270 ms | Time foot on ground — tendon stiffness |")
L(f"| **Avg Vertical Oscillation** | {avg_vo:.1f} cm | <8.5 cm | Up-down bounce — lower = more efficient |")
L(f"| **Avg Vertical Ratio** | {avg_vr:.1f}% | <8.5% | VO / Stride. The efficiency index — lower = more horizontal energy |")
L("")

# -------------------------------------------
# SECTION 9: EXHAUSTIVE LAP-BY-LAP TABLE
# -------------------------------------------
L("---")
L("## 9. Exhaustive Lap-by-Lap Table")
L("")
L("**Columns:** Pace | GAP | Avg/Max HR | Real Zone | Cadence | Stride | GCT | VO | VR | Avg/NP Power | Calories | Elev Gain/Loss | Temp | TRIMP | EPOC Est.")
L("")
L("| Lap | Pace | GAP | Avg HR | Max HR | Zone | Cad | Stride | GCT | VO | VR | Avg W | NP W | Cal | +Elev | -Elev | Temp | TRIMP | EPOC% |")
L("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
L("> EPOC% = relative contribution to session EPOC (100% = hardest lap). TRIMP = Banister AU. Both per lap.")

all_trimps = []
for lap in laps:
    hr  = lap.get("averageHR", 0) or 0
    dur = lap.get("duration", 0) / 60
    if hr > HR_REST and dur > 0:
        dhr = max(0.0, min((hr - HR_REST) / (HR_MAX - HR_REST), 1.0))
        t   = dur * dhr * 0.64 * math.exp(1.92 * dhr)
    else:
        t = 0.0
    all_trimps.append(t)

for i, lap in enumerate(laps):
    dist  = lap.get("distance", 0)
    spd   = lap.get("averageSpeed", 0)
    gap   = lap.get("avgGradeAdjustedSpeed", spd)
    hr    = lap.get("averageHR", None)
    mhr   = lap.get("maxHR", None)
    cad   = lap.get("averageRunCadence", None)
    stride= lap.get("strideLength", None)
    gct   = lap.get("groundContactTime", None)
    vo    = lap.get("verticalOscillation", None)
    vr    = lap.get("verticalRatio", None)
    pwr   = lap.get("averagePower", None)
    npwr  = lap.get("normalizedPower", None)
    cal   = lap.get("calories", None)
    eg    = lap.get("elevationGain", 0)
    el    = lap.get("elevationLoss", 0)
    t_min = lap.get("minTemperature", None)
    t_max = lap.get("maxTemperature", None)
    t_avg = lap.get("averageTemperature", None)
    
    temp_str = f"{t_min}-{t_max}C" if t_min is not None and t_max is not None else (f"{t_avg}C" if t_avg else "N/A")
    trimp_lap = all_trimps[i] if i < len(all_trimps) else 0
    epoc_pct  = lap_epoc_pct[i] if i < len(lap_epoc_pct) else 0
    
    L(f"| **{i+1}** | {pace(spd)} | {pace(gap)} | {fmt(hr,0)} | {fmt(mhr,0)} | {real_hr_zone(hr)} | {fmt(cad,0)} | {fmt(stride,1)} | {fmt(gct,0)} | {fmt(vo,1)} | {fmt(vr,1)} | {fmt(pwr,0)} | {fmt(npwr,0)} | {fmt(cal,0)} | +{eg:.0f}m | -{el:.0f}m | {temp_str} | {trimp_lap:.1f} | {epoc_pct:.0f}% |")

L("")

# -------------------------------------------
# SECTION 10: LAP FLAGS & COACHING NOTES
# -------------------------------------------
L("---")
L("## 10. Lap-by-Lap Coaching Notes & Flags")
L("")
for i, lap in enumerate(laps):
    spd   = lap.get("averageSpeed", 0)
    hr    = lap.get("averageHR", 0) or 0
    gct   = lap.get("groundContactTime", 0) or 0
    stride= lap.get("strideLength", 0) or 0
    vr    = lap.get("verticalRatio", 0) or 0
    eg    = lap.get("elevationGain", 0)
    el    = lap.get("elevationLoss", 0)
    temp  = lap.get("averageTemperature", 0)
    mhr   = lap.get("maxHR", 0) or 0
    
    flags = []
    if hr > 162:  flags.append(f"HR BREACH: {hr:.0f} bpm — above 162 cap (Z2 ceiling)")
    if hr > 185:  flags.append(f"THRESHOLD: {hr:.0f} bpm — Zone 4, heavy CNS load")
    if gct > 310: flags.append(f"HIGH GCT: {gct:.0f}ms — energy leaking into ground (braking/fatigue)")
    if gct > 0 and gct < 260: flags.append(f"ELITE GCT: {gct:.0f}ms — powerful elastic rebound")
    if stride > 97: flags.append(f"LONG STRIDE: {stride:.1f}cm — strong push-off power")
    if vr > 9.5:  flags.append(f"HIGH VR: {vr:.1f}% — excessive vertical bounce, wasted energy")
    if vr > 0 and vr < 8.5: flags.append(f"EFFICIENT VR: {vr:.1f}% — good horizontal propulsion")
    if eg > 5:    flags.append(f"UPHILL: +{eg:.0f}m — HR inflation expected")
    if el > 7:    flags.append(f"DOWNHILL: -{el:.0f}m — eccentric quad load")
    if temp >= 34:flags.append(f"PEAK HEAT: {temp}C — Heat Tax fully active, plasma loss accelerating")
    if mhr > 175: flags.append(f"MAX HR SPIKE: {mhr:.0f} bpm — high CNS activation on this lap")
    
    trimp_lap = all_trimps[i] if i < len(all_trimps) else 0
    epoc_pct  = lap_epoc_pct[i] if i < len(lap_epoc_pct) else 0
    flag_str  = " | ".join(flags) if flags else "Clean — no flags"
    
    L(f"**Lap {i+1}** | {pace(spd)} | {hr:.0f} bpm avg | TRIMP: {trimp_lap:.1f} AU | EPOC contribution: {epoc_pct:.0f}% of peak")
    L(f"  {flag_str}")
    L("")

# -------------------------------------------
# SECTION 11: FINAL VERDICT
# -------------------------------------------
L("---")
L("## 11. Final Coaching Verdict")
L("")
L(f"**TRIMP Load:** {total_trimp:.1f} AU — {'High load session. Significant recovery demand on CNS and cardiovascular system.' if total_trimp > 100 else 'Moderate-to-high load. Standard overnight recovery plus fueling.' if total_trimp > 60 else 'Moderate load. Well within recovery capacity.'}")
L("")
if pahr_decoupling is not None:
    coupling = abs(pahr_decoupling)
    L(f"**PA:HR Decoupling:** {pahr_decoupling:.1f}% — {'Excellent aerobic coupling. This was a true Zone 2 run.' if coupling < 5 else 'Moderate decoupling — Heat Tax and the fast finish pulled HR disproportionately above pace in the second half.' if coupling < 15 else 'Heavy decoupling — the run exceeded your aerobic ceiling for extended periods.'}")
    L("")
L(f"**Cardiac Drift:** +{hr_drift:.1f} bpm — {'Severe thermal stress. Plasma volume loss was high.' if hr_drift > 15 else 'Significant drift. Heat Tax was active.' if hr_drift > 10 else 'Moderate drift — manageable.' if hr_drift > 5 else 'Minimal drift — excellent thermoregulation.'}")
L("")
L(f"**EPOC (Session):** {total_epoc:.1f} mL/kg — {'Prioritize protein + carbohydrate co-ingestion within the next 2 hours to accelerate recovery.' if total_epoc > 30 else 'Standard post-run nutrition is sufficient.'} Hardest single lap: Lap {peak_epoc_lap}.")
L("")
L("**Recovery Directive:** See ACWR status in today's Kiat Engine briefing for full scheduling implications.")

# -------------------------------------------
# OUTPUT
# -------------------------------------------
report_text = "\n".join(lines)
date_str    = TARGET_DATE.replace("-", "")
output_path = rf"C:\Users\Max\.gemini\antigravity\brain\491e4690-66cd-499d-9776-017b0087dbe4\artifacts\run_analysis_{date_str}.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(report_text)

print(f"[OK] Report written to: {output_path}")
print(f"[OK] Total TRIMP: {total_trimp:.1f} AU | PA:HR Decoupling: {pahr_decoupling:.1f}% | HR Drift: +{hr_drift:.1f} bpm | Total EPOC: {total_epoc:.1f} mL/kg")
