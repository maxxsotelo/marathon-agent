"""
core_physiological_engine.py — Kiat Engine (Kiat 傑 | "To Surpass")
===============================================================
Athlete: Max | Age: 25 | Weight: 75.5 kg | Location: Marikina, PH
Hardware: Garmin Forerunner 165 | Engine: Kiat (Hokkien: to surpass, go beyond)

The Kiat Engine ingests raw Garmin telemetry and computes premium
physiological metrics that go beyond the athlete's hardware capabilities:

  1. Training Readiness Score (TRS)  — 0-100 weighted composite index
  2. Acute-to-Chronic Workload Ratio (ACWR) — Injury-risk & load balance signal
  3. Training Status Engine           — Deterministic state machine
  4. Running Economy Index (REI)      — Speed / Normalized Power efficiency
     Fatigue Biomechanics Index (FBI) — Early vs. late lap kinematic delta

  ── FORERUNNER 970-EMULATED PREMIUM METRICS ──────────────────────────────
  5. TRIMP (Banister)                — Cardiovascular training stress (AU)
     Edwards Zone-Weighted TRIMP    — Zone-multiplier cross-check
  6. PA:HR Decoupling                — Aerobic ceiling test (%)
  7. Cardiac Drift                   — Absolute & pace-corrected HR creep
     Max HR Drop                    — Walk-break / cooling event detector
  8. EPOC (Knuttgen)                 — Session-level O2 debt (mL/kg)

Author: Antigravity Agent (AI-Collaborative Systems Orchestration)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# ATHLETE CONSTANTS (Max — Marikina Tropical Conditions)
# ─────────────────────────────────────────────────────────────────────────────
HRV_FLOOR_MS        = 116     # RMSSD Baseline Floor (ms) — parasympathetic anchor
ZONE2_CAP_BPM       = 162     # Zone 2 Hard Cap (bpm) — heat-tax adjusted
LTHR_LOW_BPM        = 190     # Lactate Threshold HR lower bound
LTHR_HIGH_BPM       = 196     # Lactate Threshold HR upper bound
MAX_HR_BPM          = 206     # Verified Max HR
HR_REST_BPM         = 40      # Resting HR (midpoint of 39-42 bpm baseline)
ATHLETE_WEIGHT_KG   = 72.0    # Current bodyweight

# ACWR Safety Thresholds
ACWR_SWEET_LOW      = 0.8
ACWR_SWEET_HIGH     = 1.3
ACWR_DANGER         = 1.5     # Above this → automatic speed veto

# Readiness categories
READINESS_PRIME     = 90
READINESS_PRIMED    = 75
READINESS_MODERATE  = 50
READINESS_LOW       = 25

# Real HR Zones (from operating_manual.md Section 6) — used for TRIMP & zone time
REAL_ZONES = [
    (1, "Z1-Easy_Aerobic",  0,   161),
    (2, "Z2-Extensive",     162, 174),
    (3, "Z3-Tempo",         175, 181),
    (4, "Z4-Threshold",     182, 191),
    (5, "Z5-VO2_Max",       192, 999),
]


# ─────────────────────────────────────────────────────────────────────────────
# INPUT / OUTPUT DATA CONTAINERS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SleepData:
    """Raw sleep stage data from Garmin Connect."""
    sleep_score:        Optional[float] = None   # Native Garmin sleep score (0–100)
    total_sleep_secs:   float = 0.0              # Total sleep in seconds
    deep_sleep_secs:    float = 0.0
    light_sleep_secs:   float = 0.0
    rem_sleep_secs:     float = 0.0
    awake_secs:         float = 0.0


@dataclass
class HRVData:
    """Garmin HRV overnight metrics."""
    last_night_avg_ms:  Optional[float] = None   # Overnight RMSSD (ms)
    weekly_avg_ms:      Optional[float] = None   # 7-day rolling avg RMSSD (ms)


@dataclass
class ActivityWindow:
    """
    Encapsulates activity history for ACWR and Training Status calculations.
    'runs' is a list of dicts with keys:
      - 'date'         : datetime (UTC)
      - 'distance_km'  : float
      - 'activity_load': float  (Garmin Training Load)
      - 'activity_type': str    ('running', 'cycling', etc.)
    """
    runs: list[dict] = field(default_factory=list)


@dataclass
class LapKinematics:
    """Per-lap biomechanical data extracted from Garmin activity splits."""
    lap_index:                  int
    avg_hr:                     float = 0.0       # bpm
    max_hr:                     float = 0.0       # bpm
    avg_speed_ms:               float = 0.0       # m/s
    avg_grade_adjusted_speed_ms: float = 0.0      # Grade-adjusted speed (m/s)
    norm_power_w:               float = 0.0       # Normalized Power (W)
    cadence_spm:                float = 0.0       # Steps per minute
    stride_length_m:            float = 0.0       # Stride length in meters
    gct_ms:                     float = 0.0       # Ground Contact Time (ms)
    distance_m:                 float = 0.0       # Lap distance in meters
    duration_secs:              float = 0.0       # Lap duration in seconds
    intensity_type:             str   = "ACTIVE"  # "ACTIVE", "WARMUP", "COOLDOWN", "REST"


@dataclass
class PhysiologicalReport:
    """Final output of the Physiological Engine — all 970-emulated metrics."""
    # ── Training Readiness ──────────────────────────────────────
    trs_score:              float = 0.0
    trs_label:              str   = "Unknown"
    trs_sleep_component:    float = 0.0
    trs_recovery_component: float = 0.0
    trs_hrv_component:      float = 0.0
    trs_load_component:     float = 0.0
    trs_stress_component:   float = 0.0

    # ── ACWR ─────────────────────────────────────────────────────
    acwr:                   float = 0.0
    acute_km:               float = 0.0
    chronic_km_weekly:      float = 0.0
    acwr_zone:              str   = "Unknown"
    speed_veto:             bool  = False

    # ── Training Status ──────────────────────────────────────────
    training_status:        str   = "Unknown"
    training_status_reason: str   = ""

    # ── Running Economy ──────────────────────────────────────────
    rei:                    Optional[float] = None   # Running Economy Index
    rei_mode:               str             = "N/A"  # "power" | "hr" | "N/A"
    fbi_score:              Optional[float] = None   # Fatigue Biomechanics Index (0–100)
    fbi_cadence_delta_pct:  Optional[float] = None
    fbi_stride_delta_pct:   Optional[float] = None
    fbi_gct_delta_pct:      Optional[float] = None
    fbi_form_collapse:      bool            = False

    # ── Advanced HR & Physiological Stress (Forerunner 970-Emulated) ─────────
    trimp:                  Optional[float] = None   # Banister TRIMP (AU)
    edwards_trimp:          Optional[float] = None   # Zone-weighted TRIMP (AU)
    trimp_classification:   str             = "N/A"  # Low / Moderate / High
    pahr_decoupling:        Optional[float] = None   # PA:HR Decoupling %
    pahr_ef_first:          Optional[float] = None   # Efficiency Factor first half
    pahr_ef_second:         Optional[float] = None   # Efficiency Factor second half
    pahr_classification:    str             = "N/A"  # Coupled / Decoupled / Highly Decoupled
    hr_drift:               Optional[float] = None   # First-third vs last-third HR delta (bpm)
    cardiac_drift_trend:    Optional[float] = None   # HR per pace unit creep (bpm per m/s)
    hr_drift_classification: str            = "N/A"  # Minimal / Moderate / Significant / Severe
    max_hr_drop:            float           = 0.0    # Largest single-lap HR drop (bpm)
    max_hr_drop_lap:        Optional[int]   = None   # Lap index where drop occurred (1-based)
    epoc:                   Optional[float] = None   # Session EPOC (mL/kg), Knuttgen model
    peak_epoc_lap:          Optional[int]   = None   # Lap with highest EPOC contribution
    epoc_classification:    str             = "N/A"  # Light / Moderate / Significant / Major

    # ── Narrative Summary (for LLM injection) ────────────────────
    summary_text:           str   = ""


# ─────────────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class PhysiologicalEngine:
    """
    Kiat Engine — Forerunner 970 Software Emulation.

    Usage:
        engine = PhysiologicalEngine()
        report = engine.compute(
            sleep=sleep_data,
            hrv=hrv_data,
            recovery_hours=last_activity_recovery_hours,
            activity_end_time_utc=last_activity_end_utc,
            rolling_stress_3d=avg_3day_stress_score,
            activity_window=activity_window,
            laps=lap_kinematics_list,
        )
    """

    def compute(
        self,
        sleep: SleepData,
        hrv: HRVData,
        recovery_hours: Optional[float],
        activity_end_time_utc: Optional[datetime],
        rolling_stress_3d: Optional[float],
        activity_window: ActivityWindow,
        laps: Optional[list[LapKinematics]] = None,
    ) -> PhysiologicalReport:
        report = PhysiologicalReport()

        # ── 1. ACWR (computed first — feeds TRS load score) ──────────────────
        acwr, acute_km, chronic_weekly_km = self._compute_acwr(activity_window)
        report.acwr              = round(acwr, 3)
        report.acute_km          = round(acute_km, 2)
        report.chronic_km_weekly = round(chronic_weekly_km, 2)
        report.acwr_zone         = self._acwr_zone_label(acwr)
        report.speed_veto        = acwr > ACWR_DANGER

        # ── 2. TRAINING READINESS SCORE ──────────────────────────────────────
        s_sleep  = self._score_sleep(sleep)
        s_rec    = self._score_recovery(recovery_hours, activity_end_time_utc)
        s_hrv    = self._score_hrv(hrv)
        s_load   = self._score_load(acwr)
        s_stress = self._score_stress(rolling_stress_3d)

        trs = (
            0.30 * s_sleep +
            0.25 * s_rec   +
            0.20 * s_hrv   +
            0.15 * s_load  +
            0.10 * s_stress
        )
        report.trs_score              = round(trs, 1)
        report.trs_label              = self._trs_label(trs)
        report.trs_sleep_component    = round(s_sleep, 1)
        report.trs_recovery_component = round(s_rec, 1)
        report.trs_hrv_component      = round(s_hrv, 1)
        report.trs_load_component     = round(s_load, 1)
        report.trs_stress_component   = round(s_stress, 1)

        # ── 3. TRAINING STATUS ENGINE ─────────────────────────────────────────
        hrv_val = hrv.last_night_avg_ms
        hrv_ok  = hrv_val is not None and hrv_val >= HRV_FLOOR_MS
        stress_high = (
            rolling_stress_3d is not None and rolling_stress_3d > 60
        ) or s_stress < 50

        status, reason = self._classify_training_status(acwr, hrv_ok, stress_high)
        report.training_status        = status
        report.training_status_reason = reason

        # ── 4. RUNNING ECONOMY & FATIGUE BIOMECHANICS ─────────────────────────
        if laps:
            rei, rei_mode = self._compute_rei(laps)
            report.rei      = round(rei, 4) if rei is not None else None
            report.rei_mode = rei_mode

            fbi_score, cad_d, str_d, gct_d, form_collapse = self._compute_fbi(laps)
            report.fbi_score             = round(fbi_score, 1) if fbi_score is not None else None
            report.fbi_cadence_delta_pct = round(cad_d, 2) if cad_d is not None else None
            report.fbi_stride_delta_pct  = round(str_d, 2) if str_d is not None else None
            report.fbi_gct_delta_pct     = round(gct_d, 2) if gct_d is not None else None
            report.fbi_form_collapse     = form_collapse

        # ── 5. ADVANCED HR & PHYSIOLOGICAL STRESS METRICS ────────────────────
        if laps:
            active_laps = [l for l in laps if l.intensity_type == "ACTIVE" and l.duration_secs > 0]

            # --- TRIMP (Banister) ---
            trimp, edwards = self._compute_trimp(active_laps)
            report.trimp              = round(trimp, 1) if trimp is not None else None
            report.edwards_trimp      = round(edwards, 1) if edwards is not None else None
            report.trimp_classification = (
                "High (>100 AU)" if trimp and trimp > 100 else
                "Moderate (50-100 AU)" if trimp and trimp > 50 else
                "Low (<50 AU)" if trimp is not None else "N/A"
            )

            # --- PA:HR Decoupling ---
            dec, ef1, ef2 = self._compute_pahr_decoupling(active_laps)
            report.pahr_decoupling  = round(dec, 2) if dec is not None else None
            report.pahr_ef_first    = round(ef1 * 1000, 3) if ef1 is not None else None
            report.pahr_ef_second   = round(ef2 * 1000, 3) if ef2 is not None else None
            if dec is not None:
                abs_dec = abs(dec)
                report.pahr_classification = (
                    "COUPLED (<5%) — excellent aerobic run" if abs_dec < 5 else
                    "DECOUPLED (5-10%) — moderate drift" if abs_dec < 10 else
                    "HIGHLY DECOUPLED (>10%) — above aerobic ceiling"
                )

            # --- Cardiac Drift ---
            hr_drift, drift_trend = self._compute_cardiac_drift(active_laps)
            report.hr_drift           = round(hr_drift, 1) if hr_drift is not None else None
            report.cardiac_drift_trend = round(drift_trend, 2) if drift_trend is not None else None
            if hr_drift is not None:
                report.hr_drift_classification = (
                    "SEVERE (>15 bpm) — Dehydration + Heat Tax fully active" if hr_drift > 15 else
                    "SIGNIFICANT (10-15 bpm) — thermal stress present" if hr_drift > 10 else
                    "MODERATE (5-10 bpm) — manageable" if hr_drift > 5 else
                    "MINIMAL (<5 bpm) — excellent thermoregulation"
                )

            # --- Max HR Drop ---
            drop, drop_lap = self._compute_max_hr_drop(active_laps)
            report.max_hr_drop     = round(drop, 1)
            report.max_hr_drop_lap = drop_lap

            # --- EPOC ---
            epoc, peak_lap = self._compute_epoc(active_laps)
            report.epoc              = round(epoc, 1) if epoc is not None else None
            report.peak_epoc_lap     = peak_lap
            report.epoc_classification = (
                "MAJOR (>50 mL/kg) — Full recovery 24-48h" if epoc and epoc > 50 else
                "SIGNIFICANT (25-50 mL/kg) — Recovery 12-24h" if epoc and epoc > 25 else
                "MODERATE (10-25 mL/kg) — Standard overnight recovery" if epoc and epoc > 10 else
                "LIGHT (<10 mL/kg) — Minimal recovery impact" if epoc is not None else "N/A"
            )

        # ── 6. NARRATIVE SUMMARY ──────────────────────────────────────────────
        report.summary_text = self._build_summary(report)

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # INTERNAL COMPUTATIONS
    # ─────────────────────────────────────────────────────────────────────────

    # ── Sleep Score ──────────────────────────────────────────────────────────

    def _score_sleep(self, sleep: SleepData) -> float:
        """Use native Garmin sleep score if available, else compute heuristic."""
        if sleep.sleep_score is not None and sleep.sleep_score > 0:
            return float(sleep.sleep_score)   # Already 0–100

        # Fallback: physiological sleep heuristic
        ref_total = sleep.total_sleep_secs
        if ref_total <= 0:
            ref_total = (
                sleep.deep_sleep_secs + sleep.light_sleep_secs +
                sleep.rem_sleep_secs  + sleep.awake_secs
            )
        if ref_total <= 0:
            return 50.0  # Unknown → neutral

        p_deep  = (sleep.deep_sleep_secs / ref_total) * 100
        p_rem   = (sleep.rem_sleep_secs  / ref_total) * 100
        p_awake = (sleep.awake_secs      / ref_total) * 100
        h_sleep = ref_total / 3600.0

        s_dur   = self._score_duration(h_sleep)
        s_deep  = self._score_deep(p_deep)
        s_rem   = self._score_rem(p_rem)
        s_awake = self._score_awake(p_awake)

        return 0.40 * s_dur + 0.20 * s_deep + 0.20 * s_rem + 0.20 * s_awake

    @staticmethod
    def _score_duration(h_sleep: float) -> float:
        """Target: 8 hours. Penalty: -15 pts per hour off target."""
        return max(0.0, 100.0 - 15.0 * abs(h_sleep - 8.0))

    @staticmethod
    def _score_deep(p_deep: float) -> float:
        """Target band: 15–25%."""
        if 15 <= p_deep <= 25:
            return 100.0
        if p_deep < 15:
            return (p_deep / 15) * 100
        return max(0.0, 100.0 - 5.0 * (p_deep - 25))

    @staticmethod
    def _score_rem(p_rem: float) -> float:
        """Target band: 20–25%."""
        if 20 <= p_rem <= 25:
            return 100.0
        if p_rem < 20:
            return (p_rem / 20) * 100
        return max(0.0, 100.0 - 5.0 * (p_rem - 25))

    @staticmethod
    def _score_awake(p_awake: float) -> float:
        """Target: ≤ 5%. Penalty: -4 pts per % above 5."""
        return max(0.0, 100.0 - 4.0 * max(0.0, p_awake - 5.0))

    # ── Recovery Time ────────────────────────────────────────────────────────

    @staticmethod
    def _score_recovery(
        recovery_hours: Optional[float],
        activity_end_time_utc: Optional[datetime],
    ) -> float:
        """
        Model current remaining recovery as a linear decay from the last
        activity's end time. 0 remaining hours = full score (100),
        48+ remaining hours = score 0.
        """
        if recovery_hours is None or recovery_hours <= 0:
            return 100.0  # No outstanding recovery needed

        if activity_end_time_utc is None:
            remaining = recovery_hours / 2.0
        else:
            now_utc = datetime.now(timezone.utc)
            elapsed_hours = (now_utc - activity_end_time_utc).total_seconds() / 3600.0
            remaining = max(0.0, recovery_hours - elapsed_hours)

        return max(0.0, 100.0 - (remaining / 48.0) * 100.0)

    # ── HRV Score ────────────────────────────────────────────────────────────

    @staticmethod
    def _score_hrv(hrv: HRVData) -> float:
        """
        Score based on overnight RMSSD vs. the 116 ms baseline floor.
        >= 116 ms → 100. Every ms below 116 loses 3 points.
        """
        hrv_val = hrv.last_night_avg_ms
        if hrv_val is None:
            return 60.0  # Unknown — mildly penalised, not catastrophic
        if hrv_val >= HRV_FLOOR_MS:
            return 100.0
        return max(0.0, 100.0 - 3.0 * (HRV_FLOOR_MS - hrv_val))

    # ── Load (ACWR-based) ────────────────────────────────────────────────────

    @staticmethod
    def _score_load(acwr: float) -> float:
        """
        100 inside the sweet zone (0.8–1.3).
        Falls off linearly outside the zone.
        """
        if ACWR_SWEET_LOW <= acwr <= ACWR_SWEET_HIGH:
            return 100.0
        if acwr < ACWR_SWEET_LOW:
            if ACWR_SWEET_LOW == 0:
                return 100.0
            return max(0.0, 100.0 - 100.0 * (ACWR_SWEET_LOW - acwr) / ACWR_SWEET_LOW)
        # acwr > sweet high
        return max(0.0, 100.0 - 100.0 * (acwr - ACWR_SWEET_HIGH) / 0.7)

    # ── Stress Score ─────────────────────────────────────────────────────────

    @staticmethod
    def _score_stress(rolling_stress_3d: Optional[float]) -> float:
        """
        Garmin stress 0–100. Target ≤ 25 for full marks.
        Penalty: -2 pts per stress unit above 25.
        """
        if rolling_stress_3d is None:
            return 70.0  # Unknown → slightly below optimal
        return max(0.0, 100.0 - 2.0 * max(0.0, rolling_stress_3d - 25.0))

    # ── TRS Label ────────────────────────────────────────────────────────────

    @staticmethod
    def _trs_label(trs: float) -> str:
        if trs >= READINESS_PRIME:
            return "Prime"
        if trs >= READINESS_PRIMED:
            return "Primed"
        if trs >= READINESS_MODERATE:
            return "Moderate"
        if trs >= READINESS_LOW:
            return "Low"
        return "Depleted"

    # ── ACWR ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_acwr(window: ActivityWindow) -> tuple[float, float, float]:
        """
        Compute ACWR from rolling activity data.
        Returns (acwr, acute_km, chronic_weekly_km).
        """
        now_utc = datetime.now(timezone.utc)
        cutoff_7d  = now_utc - timedelta(days=7)
        cutoff_28d = now_utc - timedelta(days=28)

        runs_28d = [
            r for r in window.runs
            if r.get('activity_type') in ('running', 'treadmill_running', 'trail_running', 'indoor_running')
            and r.get('date') is not None
            and r['date'] >= cutoff_28d
        ]

        acute_km  = sum(
            r['distance_km'] for r in runs_28d if r['date'] >= cutoff_7d
        )
        total_28d_km = sum(r['distance_km'] for r in runs_28d)
        chronic_weekly_km = total_28d_km / 4.0   # Normalize to per-week

        if chronic_weekly_km <= 0:
            acwr = 0.0
        else:
            acwr = acute_km / chronic_weekly_km

        return acwr, acute_km, chronic_weekly_km

    @staticmethod
    def _acwr_zone_label(acwr: float) -> str:
        if acwr > ACWR_DANGER:
            return f"[!! DANGER] ({acwr:.2f}) -- Auto Speed Veto Active"
        if acwr > ACWR_SWEET_HIGH:
            return f"[! High] ({acwr:.2f}) -- Reduce volume next 3-5 days"
        if acwr >= ACWR_SWEET_LOW:
            return f"[OK Sweet Spot] ({acwr:.2f}) -- Load is optimal"
        if acwr > 0:
            return f"[Low] ({acwr:.2f}) -- Undertraining or taper"
        return "N/A -- Insufficient data"

    # ── Training Status Engine ────────────────────────────────────────────────

    @staticmethod
    def _classify_training_status(
        acwr: float,
        hrv_ok: bool,
        stress_high: bool,
    ) -> tuple[str, str]:
        """
        Deterministic rule-based state machine.
        Returns (status_label, reason_string).
        """
        if not hrv_ok and acwr >= 1.0:
            return (
                "Unproductive",
                "HRV is depressed below 116 ms baseline despite high training load. "
                "Physiological adaptation is stalling. Reduce intensity until HRV recovers."
            )
        if (not hrv_ok or stress_high) and acwr >= ACWR_SWEET_HIGH:
            return (
                "Strained / Overreaching",
                f"HRV below floor {'and ' if not hrv_ok else ''}high psychological stress detected "
                f"during a high-load block (ACWR {acwr:.2f}). CNS fatigue risk. Mandatory recovery pivot."
            )
        if hrv_ok and acwr > ACWR_SWEET_HIGH:
            return (
                "Productive",
                f"HRV is balanced and load is slightly elevated (ACWR {acwr:.2f}). "
                "Training stimulus is being absorbed - continue current trajectory."
            )
        if hrv_ok and ACWR_SWEET_LOW <= acwr <= ACWR_SWEET_HIGH:
            return (
                "Productive",
                f"HRV is balanced and workload is in the sweet spot (ACWR {acwr:.2f}). "
                "Ideal training state - positive adaptation is occurring."
            )
        if hrv_ok and 0.3 <= acwr < ACWR_SWEET_LOW:
            return (
                "Peaking / Tapering",
                f"Volume is reduced (ACWR {acwr:.2f}) and HRV is elevated. "
                "Physiological signature of a taper or early peak phase."
            )
        if hrv_ok and acwr < 0.3:
            return (
                "Recovery",
                f"Low training load (ACWR {acwr:.2f}) with balanced HRV. "
                "Active rest phase - structural repair and neuromuscular recharge underway."
            )
        # Fallback
        return (
            "Maintaining",
            f"Stable HRV and moderate load (ACWR {acwr:.2f}). "
            "Maintenance stimulus - no net fitness gain or loss expected."
        )

    # ── Running Economy Index (REI) ───────────────────────────────────────────

    def _compute_rei(
        self,
        laps: list[LapKinematics],
    ) -> tuple[Optional[float], str]:
        """
        REI = Speed (m/s) / Normalized Power (W) × 1000  [Power mode]
        Fallback: Speed (m/s) / HR (bpm) × 1000          [HR mode]

        Only computed over active Zone 2 laps (HR 162-174 bpm).
        Returns (rei_value, mode_label).
        """
        zone2_laps = [
            l for l in laps
            if l.intensity_type == "ACTIVE"
            and 162 <= l.avg_hr <= ZONE2_CAP_BPM
        ]
        if not zone2_laps:
            zone2_laps = [l for l in laps if l.intensity_type == "ACTIVE"]
        if not zone2_laps:
            return None, "N/A"

        # Prefer Normalized Power
        power_laps = [l for l in zone2_laps if l.norm_power_w > 0]
        if power_laps:
            avg_speed = sum(l.avg_speed_ms for l in power_laps) / len(power_laps)
            avg_np    = sum(l.norm_power_w for l in power_laps) / len(power_laps)
            if avg_np > 0:
                return (avg_speed / avg_np) * 1000, "power"

        # Fallback to HR-based economy
        hr_laps = [l for l in zone2_laps if l.avg_hr > 0]
        if hr_laps:
            avg_speed = sum(l.avg_speed_ms for l in hr_laps) / len(hr_laps)
            avg_hr    = sum(l.avg_hr for l in hr_laps) / len(hr_laps)
            if avg_hr > 0:
                return (avg_speed / avg_hr) * 1000, "hr"

        return None, "N/A"

    # ── Fatigue Biomechanics Index (FBI) ──────────────────────────────────────

    @staticmethod
    def _compute_fbi(
        laps: list[LapKinematics],
    ) -> tuple[Optional[float], Optional[float], Optional[float], Optional[float], bool]:
        """
        Compare kinematics of early laps (1–3) vs. late active laps.
        Returns (fbi_score, cadence_delta%, stride_delta%, gct_delta%, form_collapse).
        """
        active_laps = sorted(
            [l for l in laps if l.intensity_type == "ACTIVE"],
            key=lambda l: l.lap_index
        )
        if len(active_laps) < 4:
            return None, None, None, None, False

        early = active_laps[:3]
        late  = active_laps[-3:]

        def avg(lst, attr):
            vals = [getattr(l, attr) for l in lst if getattr(l, attr, 0) > 0]
            return sum(vals) / len(vals) if vals else 0.0

        def delta_pct(early_val, late_val):
            if early_val == 0:
                return 0.0
            return ((late_val - early_val) / early_val) * 100.0

        cad_early  = avg(early, 'cadence_spm')
        cad_late   = avg(late,  'cadence_spm')
        str_early  = avg(early, 'stride_length_m')
        str_late   = avg(late,  'stride_length_m')
        gct_early  = avg(early, 'gct_ms')
        gct_late   = avg(late,  'gct_ms')

        cad_delta = delta_pct(cad_early, cad_late)
        str_delta = delta_pct(str_early, str_late)
        gct_delta = delta_pct(gct_early, gct_late)

        # Penalties (positive penalty = worse score)
        p_cad    = max(0.0, -cad_delta * 10)   # Penalty for cadence DROP
        p_stride = max(0.0, -str_delta * 15)   # Penalty for stride LENGTH drop
        p_gct    = max(0.0,  gct_delta * 5)    # Penalty for GCT INCREASE (slower push-off)

        fbi = max(0.0, 100.0 - p_cad - p_stride - p_gct)
        form_collapse = fbi < 70.0

        return fbi, cad_delta, str_delta, gct_delta, form_collapse

    # ─────────────────────────────────────────────────────────────────────────
    # ADVANCED HR & PHYSIOLOGICAL STRESS COMPUTATIONS
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _hr_zone_num(hr: float) -> int:
        """Return Max's real HR zone number (1–5) for a given HR value."""
        if hr <= 0:
            return 0
        for num, _, lo, hi in REAL_ZONES:
            if lo <= hr <= hi:
                return num
        return 5

    @staticmethod
    def _compute_trimp(
        laps: list[LapKinematics],
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Banister's Training Impulse (1991) and Edwards Zone-Weighted TRIMP.

        Banister TRIMP:
          For each lap: TRIMP = duration_min × ΔHR_ratio × 0.64 × e^(1.92 × ΔHR_ratio)
          ΔHR_ratio = (HR_avg - HR_rest) / (HR_max - HR_rest), clamped 0–1.

        Edwards TRIMP:
          Duration_in_zone_min × zone_number (1×Z1 … 5×Z5) summed over all laps.

        Returns (banister_trimp, edwards_trimp) in arbitrary units (AU).
        """
        hr_range = MAX_HR_BPM - HR_REST_BPM
        if hr_range <= 0:
            return None, None

        banister = 0.0
        edwards  = 0.0

        for lap in laps:
            hr  = lap.avg_hr
            dur = lap.duration_secs / 60.0  # minutes
            if hr <= HR_REST_BPM or dur <= 0:
                continue
            dhr = (hr - HR_REST_BPM) / hr_range
            dhr = max(0.0, min(dhr, 1.0))
            banister += dur * dhr * 0.64 * math.exp(1.92 * dhr)

            # Zone for Edwards
            z = 0
            for num, _, lo, hi in REAL_ZONES:
                if lo <= hr <= hi:
                    z = num
                    break
            if z == 0:
                z = 5
            edwards += dur * z

        return (banister if banister > 0 else None,
                edwards  if edwards  > 0 else None)

    @staticmethod
    def _compute_pahr_decoupling(
        laps: list[LapKinematics],
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        PA:HR Aerobic Decoupling.
        Efficiency Factor (EF) = GAP (m/s) / Avg HR (bpm) for each lap.
        Decoupling = (EF_first_half - EF_second_half) / EF_first_half × 100.
        < 5% = coupled aerobic run.  > 5% = HR drifting from effort.

        Returns (decoupling_pct, ef_first, ef_second).
        """
        n_half = len(laps) // 2
        if n_half == 0:
            return None, None, None

        first_half  = laps[:n_half]
        second_half = laps[n_half:]

        def avg_ef(lap_list):
            efs = []
            for l in lap_list:
                gap = l.avg_grade_adjusted_speed_ms if l.avg_grade_adjusted_speed_ms > 0 else l.avg_speed_ms
                hr  = l.avg_hr
                if hr > 0 and gap > 0:
                    efs.append(gap / hr)
            return sum(efs) / len(efs) if efs else None

        ef1 = avg_ef(first_half)
        ef2 = avg_ef(second_half)

        if ef1 is None or ef2 is None or ef1 <= 0:
            return None, ef1, ef2

        decoupling = ((ef1 - ef2) / ef1) * 100.0
        return decoupling, ef1, ef2

    @staticmethod
    def _compute_cardiac_drift(
        laps: list[LapKinematics],
    ) -> tuple[Optional[float], Optional[float]]:
        """
        Cardiac Drift.
        hr_drift:       Average HR of last third vs first third of active laps (bpm delta).
        drift_trend:    HR/pace ratio (bpm per m/s) comparing first vs last quarter.
                        Positive = HR rising relative to pace (heat/plasma loss effect).

        Returns (hr_drift_bpm, cardiac_drift_index).
        """
        n = len(laps)
        if n < 3:
            return None, None

        third = max(1, n // 3)
        first_third = laps[:third]
        last_third  = laps[-third:]

        first_avg_hr = sum(l.avg_hr for l in first_third) / len(first_third)
        last_avg_hr  = sum(l.avg_hr for l in last_third)  / len(last_third)
        hr_drift = last_avg_hr - first_avg_hr

        # Cardiac Drift Index: bpm per m/s (HR per unit of pace)
        drift_ratios = []
        for lap in laps:
            spd = lap.avg_speed_ms if lap.avg_speed_ms > 0 else 0
            hr  = lap.avg_hr
            if spd > 0 and hr > 0:
                drift_ratios.append(hr / spd)

        drift_trend = None
        if len(drift_ratios) >= 4:
            q = len(drift_ratios) // 4
            first_q = sum(drift_ratios[:q]) / q
            last_q  = sum(drift_ratios[-q:]) / q
            drift_trend = last_q - first_q  # positive = HR rising relative to pace

        return hr_drift, drift_trend

    @staticmethod
    def _compute_max_hr_drop(
        laps: list[LapKinematics],
    ) -> tuple[float, Optional[int]]:
        """
        Detect the largest consecutive-lap HR drop among active laps.
        Identifies walk breaks, cooling events, or significant downhills.

        Returns (max_drop_bpm, lap_index_1based_where_drop_occurred).
        """
        max_drop     = 0.0
        max_drop_lap = None

        for i in range(1, len(laps)):
            prev_hr = laps[i - 1].avg_hr
            curr_hr = laps[i].avg_hr
            if prev_hr > 0 and curr_hr > 0:
                drop = prev_hr - curr_hr
                if drop > max_drop:
                    max_drop     = drop
                    max_drop_lap = laps[i].lap_index + 1  # 1-based, pointing at the lap where drop occurred

        return max_drop, max_drop_lap

    @staticmethod
    def _compute_epoc(
        laps: list[LapKinematics],
    ) -> tuple[Optional[float], Optional[int]]:
        """
        EPOC Estimate — Knuttgen model.
        Session EPOC (mL/kg) = 0.096 × e^(0.0284 × %HRmax) × duration_min
        where %HRmax is computed from the session-average HR.

        Per-lap relative EPOC score = (HR/HRmax)² × duration_min
        (normalized to 100% for the peak lap — used to identify which lap drove the debt).

        Returns (session_epoc_ml_per_kg, peak_epoc_lap_1based).
        """
        if not laps:
            return None, None

        total_dur_min = sum(l.duration_secs / 60.0 for l in laps)
        total_hr_sum  = sum(l.avg_hr * (l.duration_secs / 60.0) for l in laps)
        if total_dur_min <= 0:
            return None, None

        session_avg_hr  = total_hr_sum / total_dur_min
        pct_hrmax       = (session_avg_hr / MAX_HR_BPM) * 100.0
        session_epoc    = 0.096 * math.exp(0.0284 * pct_hrmax) * total_dur_min

        # Per-lap relative EPOC score
        lap_scores = []
        for lap in laps:
            hr  = lap.avg_hr
            dur = lap.duration_secs / 60.0
            score = (hr / MAX_HR_BPM) ** 2 * dur if hr > 0 else 0.0
            lap_scores.append(score)

        if lap_scores:
            max_score    = max(lap_scores)
            peak_idx     = lap_scores.index(max_score)
            peak_lap_num = laps[peak_idx].lap_index + 1  # 1-based
        else:
            peak_lap_num = None

        return session_epoc, peak_lap_num

    # ── Narrative Summary (LLM-ready string) ─────────────────────────────────

    @staticmethod
    def _build_summary(r: PhysiologicalReport) -> str:
        """
        Builds a structured, LLM-injected string summarising all Kiat Engine
        premium metrics. Designed to be pasted directly into an AI system prompt.
        """
        veto_str = (
            "[!! AUTO VETO] Speed/intensity sessions are BLOCKED today."
            if r.speed_veto
            else "[OK] No automatic veto triggered."
        )

        rei_str = (
            f"{r.rei:.4f} ({r.rei_mode}-based)" if r.rei is not None
            else "N/A -- insufficient Zone 2 lap data"
        )
        fbi_str = (
            f"{r.fbi_score:.1f}/100 | Cadence d: {r.fbi_cadence_delta_pct:+.1f}% | "
            f"Stride d: {r.fbi_stride_delta_pct:+.1f}% | GCT d: {r.fbi_gct_delta_pct:+.1f}% | "
            f"Form Collapse: {'YES [!!]' if r.fbi_form_collapse else 'NO [OK]'}"
            if r.fbi_score is not None
            else "N/A -- insufficient lap data (need >= 4 active laps)"
        )

        # Advanced HR block
        trimp_str = (
            f"Banister: {r.trimp:.1f} AU | Edwards: {r.edwards_trimp:.1f} AU | {r.trimp_classification}"
            if r.trimp is not None else "N/A -- no active laps with duration data"
        )
        pahr_str = (
            f"{r.pahr_decoupling:.1f}% | EF First Half: {r.pahr_ef_first} | "
            f"EF Second Half: {r.pahr_ef_second} | {r.pahr_classification}"
            if r.pahr_decoupling is not None else "N/A -- insufficient lap data"
        )
        drift_str = (
            f"Absolute Drift: +{r.hr_drift:.1f} bpm | "
            f"Cardiac Drift Index: {f'+{r.cardiac_drift_trend:.2f}' if r.cardiac_drift_trend is not None else 'N/A'} bpm/(m/s) | "
            f"{r.hr_drift_classification}"
            if r.hr_drift is not None else "N/A -- insufficient lap data"
        )
        drop_str = (
            f"-{r.max_hr_drop:.0f} bpm at Lap {r.max_hr_drop_lap} | "
            f"{'Likely walk break or cooling event' if r.max_hr_drop > 10 else 'Normal pace variation'}"
            if r.max_hr_drop > 0 else "N/A"
        )
        epoc_str = (
            f"{r.epoc:.1f} mL/kg | Hardest Lap: #{r.peak_epoc_lap} | {r.epoc_classification}"
            if r.epoc is not None else "N/A -- no lap data"
        )

        return f"""
=======================================================
   KIAT ENGINE -- PHYSIOLOGICAL METRICS
   Athlete: Max | Weight: {ATHLETE_WEIGHT_KG} kg | HRV Floor: {HRV_FLOOR_MS} ms | HR Rest: {HR_REST_BPM} bpm | HR Max: {MAX_HR_BPM} bpm
=======================================================

-- 1. TRAINING READINESS SCORE ----------------------
   Overall Score:  {r.trs_score:.1f} / 100 -- {r.trs_label}
   Sleep History   (30%): {r.trs_sleep_component:.1f}
   Recovery Time   (25%): {r.trs_recovery_component:.1f}
   HRV Status      (20%): {r.trs_hrv_component:.1f}
   Acute Load      (15%): {r.trs_load_component:.1f}
   Stress History  (10%): {r.trs_stress_component:.1f}

-- 2. ACUTE-TO-CHRONIC WORKLOAD RATIO (ACWR) --------
   Acute Load  (7d):  {r.acute_km:.2f} km
   Chronic Load (avg weekly 28d): {r.chronic_km_weekly:.2f} km/week
   ACWR:        {r.acwr:.3f}
   Zone:        {r.acwr_zone}
   {veto_str}

-- 3. TRAINING STATUS --------------------------------
   Status:  {r.training_status}
   Reason:  {r.training_status_reason}

-- 4. RUNNING ECONOMY & BIOMECHANICS -----------------
   REI (Running Economy Index): {rei_str}
   FBI (Fatigue Biomechanics Index): {fbi_str}

-- 5. ADVANCED HR & PHYSIOLOGICAL STRESS (970-Emulated) --
   TRIMP (Training Stress):  {trimp_str}
   PA:HR Decoupling:         {pahr_str}
   Cardiac Drift:            {drift_str}
   Max HR Drop:              {drop_str}
   EPOC (O2 Recovery Debt):  {epoc_str}
=======================================================
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY: Parse Raw Garmin API dicts → Engine Input Objects
# ─────────────────────────────────────────────────────────────────────────────

def parse_sleep_data(sleep_dto: dict) -> SleepData:
    """Convert Garmin's raw sleep API dict into SleepData."""
    total_sleep_secs = (
        sleep_dto.get('sleepTimeInSeconds') or
        sleep_dto.get('totalSleepSeconds') or 0.0
    )
    return SleepData(
        sleep_score       = sleep_dto.get('sleepScore'),
        total_sleep_secs  = float(total_sleep_secs),
        deep_sleep_secs   = float(
            sleep_dto.get('deepSleepSeconds') or
            sleep_dto.get('deepSleepDurationInSeconds') or 0
        ),
        light_sleep_secs  = float(
            sleep_dto.get('lightSleepSeconds') or
            sleep_dto.get('lightSleepDurationInSeconds') or 0
        ),
        rem_sleep_secs    = float(
            sleep_dto.get('remSleepSeconds') or
            sleep_dto.get('remSleepInSeconds') or 0
        ),
        awake_secs        = float(
            sleep_dto.get('awakeSleepSeconds') or
            sleep_dto.get('awakeDurationInSeconds') or 0
        ),
    )


def parse_hrv_data(hrv_summary: dict) -> HRVData:
    """Convert Garmin HRV summary dict into HRVData."""
    return HRVData(
        last_night_avg_ms = hrv_summary.get('lastNightAvg'),
        weekly_avg_ms     = hrv_summary.get('weeklyAvg'),
    )


def parse_activity_window(activities: list[dict]) -> ActivityWindow:
    """
    Convert a list of raw Garmin activity dicts into an ActivityWindow.
    Expects activities sorted newest-first (Garmin default).
    """
    runs = []
    for act in activities:
        act_type = act.get('activityType', {}).get('typeKey', '')
        start_raw = act.get('startTimeLocal') or act.get('startTimeGmt') or ''
        act_date = None
        if start_raw:
            try:
                dt_naive = datetime.fromisoformat(start_raw[:19].replace(' ', 'T'))
                act_date = dt_naive.replace(tzinfo=timezone.utc) - timedelta(hours=8)
            except ValueError:
                pass
        dist_km = (act.get('distance') or 0) / 1000.0
        act_load = act.get('activityTrainingLoad') or 0.0
        runs.append({
            'date':          act_date,
            'distance_km':   dist_km,
            'activity_load': float(act_load),
            'activity_type': act_type,
        })
    return ActivityWindow(runs=runs)


def parse_laps(lap_dtos: list[dict]) -> list[LapKinematics]:
    """Convert Garmin split lapDTOs into a list of LapKinematics."""
    laps = []
    for lap in lap_dtos:
        stride_raw = lap.get('strideLength') or 0
        stride_m   = stride_raw / 100.0 if stride_raw > 10 else float(stride_raw)

        avg_spd = float(lap.get('averageSpeed') or 0)
        gap_spd = float(lap.get('avgGradeAdjustedSpeed') or 0)

        laps.append(LapKinematics(
            lap_index                   = lap.get('lapIndex', 0),
            avg_hr                      = float(lap.get('averageHR') or 0),
            max_hr                      = float(lap.get('maxHR') or 0),
            avg_speed_ms                = avg_spd,
            avg_grade_adjusted_speed_ms = gap_spd if gap_spd > 0 else avg_spd,
            norm_power_w                = float(lap.get('normalizedPower') or 0),
            cadence_spm                 = float(lap.get('averageRunCadence') or 0),
            stride_length_m             = stride_m,
            gct_ms                      = float(lap.get('groundContactTime') or 0),
            distance_m                  = float(lap.get('distance') or 0),
            duration_secs               = float(lap.get('duration') or 0),
            intensity_type              = lap.get('intensityType', 'ACTIVE'),
        ))
    return laps


# ─────────────────────────────────────────────────────────────────────────────
# QUICK SELF-TEST (run directly to sanity-check engine math)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from datetime import timezone

    engine = PhysiologicalEngine()

    # Simulate a healthy, well-recovered athlete
    test_sleep = SleepData(
        sleep_score=None,
        total_sleep_secs=27000,   # 7.5 hours
        deep_sleep_secs=4500,     # ~17%
        light_sleep_secs=13500,
        rem_sleep_secs=6300,      # ~23%
        awake_secs=2700,          # 10%
    )
    test_hrv = HRVData(last_night_avg_ms=128, weekly_avg_ms=121)

    # Fake 28d run history: ~42 km over 4 weeks
    now_utc = datetime.now(timezone.utc)
    fake_runs = []
    distances = [4, 6, 8, 4, 5, 7, 8]   # Last 7 days
    for i, d in enumerate(distances):
        fake_runs.append({
            'date': now_utc - timedelta(days=i),
            'distance_km': d,
            'activity_load': 50.0,
            'activity_type': 'running',
        })
    for i in range(7, 28):
        fake_runs.append({
            'date': now_utc - timedelta(days=i),
            'distance_km': 5.5,
            'activity_load': 45.0,
            'activity_type': 'running',
        })

    fake_window = ActivityWindow(runs=fake_runs)

    # Fake lap data — simulate a 21km long run with progressive cardiac drift
    # Realistic: 1km laps at Zone 2, ~6:20/km, 300-320s per lap
    # HR creeps from 152 to 164, cadence drops slightly, GCT increases slightly
    fake_laps = [
        # (lap_idx, avg_hr, max_hr, speed_ms, gap_ms, np_w, cad, stride_m, gct, dist_m, dur_s)
        LapKinematics(0,  avg_hr=150, max_hr=156, avg_speed_ms=2.63, avg_grade_adjusted_speed_ms=2.65, norm_power_w=0, cadence_spm=172, stride_length_m=1.53, gct_ms=262, distance_m=1000, duration_secs=380, intensity_type="WARMUP"),
        LapKinematics(1,  avg_hr=152, max_hr=157, avg_speed_ms=2.65, avg_grade_adjusted_speed_ms=2.67, norm_power_w=0, cadence_spm=172, stride_length_m=1.54, gct_ms=263, distance_m=1000, duration_secs=378, intensity_type="ACTIVE"),
        LapKinematics(2,  avg_hr=153, max_hr=158, avg_speed_ms=2.64, avg_grade_adjusted_speed_ms=2.66, norm_power_w=0, cadence_spm=171, stride_length_m=1.54, gct_ms=265, distance_m=1000, duration_secs=379, intensity_type="ACTIVE"),
        LapKinematics(3,  avg_hr=154, max_hr=159, avg_speed_ms=2.64, avg_grade_adjusted_speed_ms=2.65, norm_power_w=0, cadence_spm=171, stride_length_m=1.53, gct_ms=266, distance_m=1000, duration_secs=379, intensity_type="ACTIVE"),
        LapKinematics(4,  avg_hr=154, max_hr=160, avg_speed_ms=2.63, avg_grade_adjusted_speed_ms=2.64, norm_power_w=0, cadence_spm=170, stride_length_m=1.53, gct_ms=268, distance_m=1000, duration_secs=380, intensity_type="ACTIVE"),
        LapKinematics(5,  avg_hr=155, max_hr=160, avg_speed_ms=2.63, avg_grade_adjusted_speed_ms=2.63, norm_power_w=0, cadence_spm=170, stride_length_m=1.52, gct_ms=269, distance_m=1000, duration_secs=380, intensity_type="ACTIVE"),
        LapKinematics(6,  avg_hr=156, max_hr=161, avg_speed_ms=2.62, avg_grade_adjusted_speed_ms=2.63, norm_power_w=0, cadence_spm=170, stride_length_m=1.52, gct_ms=270, distance_m=1000, duration_secs=381, intensity_type="ACTIVE"),
        LapKinematics(7,  avg_hr=157, max_hr=162, avg_speed_ms=2.62, avg_grade_adjusted_speed_ms=2.62, norm_power_w=0, cadence_spm=169, stride_length_m=1.52, gct_ms=272, distance_m=1000, duration_secs=381, intensity_type="ACTIVE"),
        LapKinematics(8,  avg_hr=157, max_hr=162, avg_speed_ms=2.61, avg_grade_adjusted_speed_ms=2.62, norm_power_w=0, cadence_spm=169, stride_length_m=1.51, gct_ms=273, distance_m=1000, duration_secs=383, intensity_type="ACTIVE"),
        LapKinematics(9,  avg_hr=158, max_hr=163, avg_speed_ms=2.61, avg_grade_adjusted_speed_ms=2.61, norm_power_w=0, cadence_spm=169, stride_length_m=1.51, gct_ms=274, distance_m=1000, duration_secs=383, intensity_type="ACTIVE"),
        LapKinematics(10, avg_hr=159, max_hr=164, avg_speed_ms=2.60, avg_grade_adjusted_speed_ms=2.61, norm_power_w=0, cadence_spm=168, stride_length_m=1.50, gct_ms=276, distance_m=1000, duration_secs=385, intensity_type="ACTIVE"),
        LapKinematics(11, avg_hr=159, max_hr=164, avg_speed_ms=2.60, avg_grade_adjusted_speed_ms=2.60, norm_power_w=0, cadence_spm=168, stride_length_m=1.50, gct_ms=277, distance_m=1000, duration_secs=385, intensity_type="ACTIVE"),
        LapKinematics(12, avg_hr=160, max_hr=165, avg_speed_ms=2.59, avg_grade_adjusted_speed_ms=2.60, norm_power_w=0, cadence_spm=167, stride_length_m=1.49, gct_ms=279, distance_m=1000, duration_secs=386, intensity_type="ACTIVE"),
        LapKinematics(13, avg_hr=161, max_hr=166, avg_speed_ms=2.58, avg_grade_adjusted_speed_ms=2.59, norm_power_w=0, cadence_spm=167, stride_length_m=1.49, gct_ms=281, distance_m=1000, duration_secs=387, intensity_type="ACTIVE"),
        LapKinematics(14, avg_hr=161, max_hr=166, avg_speed_ms=2.58, avg_grade_adjusted_speed_ms=2.59, norm_power_w=0, cadence_spm=166, stride_length_m=1.48, gct_ms=282, distance_m=1000, duration_secs=388, intensity_type="ACTIVE"),
        LapKinematics(15, avg_hr=162, max_hr=167, avg_speed_ms=2.57, avg_grade_adjusted_speed_ms=2.58, norm_power_w=0, cadence_spm=166, stride_length_m=1.48, gct_ms=284, distance_m=1000, duration_secs=389, intensity_type="ACTIVE"),
        LapKinematics(16, avg_hr=162, max_hr=168, avg_speed_ms=2.57, avg_grade_adjusted_speed_ms=2.57, norm_power_w=0, cadence_spm=165, stride_length_m=1.47, gct_ms=285, distance_m=1000, duration_secs=390, intensity_type="ACTIVE"),
        LapKinematics(17, avg_hr=163, max_hr=168, avg_speed_ms=2.56, avg_grade_adjusted_speed_ms=2.57, norm_power_w=0, cadence_spm=165, stride_length_m=1.47, gct_ms=287, distance_m=1000, duration_secs=391, intensity_type="ACTIVE"),
        LapKinematics(18, avg_hr=164, max_hr=169, avg_speed_ms=2.55, avg_grade_adjusted_speed_ms=2.56, norm_power_w=0, cadence_spm=164, stride_length_m=1.46, gct_ms=289, distance_m=1000, duration_secs=392, intensity_type="ACTIVE"),
        LapKinematics(19, avg_hr=165, max_hr=170, avg_speed_ms=2.55, avg_grade_adjusted_speed_ms=2.56, norm_power_w=0, cadence_spm=164, stride_length_m=1.46, gct_ms=291, distance_m=1000, duration_secs=392, intensity_type="ACTIVE"),
        LapKinematics(20, avg_hr=147, max_hr=160, avg_speed_ms=2.30, avg_grade_adjusted_speed_ms=2.32, norm_power_w=0, cadence_spm=162, stride_length_m=1.42, gct_ms=295, distance_m=330,  duration_secs=143, intensity_type="COOLDOWN"),
    ]

    report = engine.compute(
        sleep=test_sleep,
        hrv=test_hrv,
        recovery_hours=18,
        activity_end_time_utc=now_utc - timedelta(hours=10),
        rolling_stress_3d=30.0,
        activity_window=fake_window,
        laps=fake_laps,
    )

    print(report.summary_text)
    print(f"\nRaw TRS:          {report.trs_score}")
    print(f"Training Status:  {report.training_status}")
    print(f"ACWR:             {report.acwr}")
    print(f"Speed Veto:       {report.speed_veto}")
    print(f"FBI Score:        {report.fbi_score}")
    print(f"Form Collapse:    {report.fbi_form_collapse}")
    print(f"TRIMP (Banister): {report.trimp} AU")
    print(f"Edwards TRIMP:    {report.edwards_trimp} AU")
    print(f"PA:HR Decoupling: {report.pahr_decoupling}%")
    print(f"HR Drift:         {report.hr_drift} bpm")
    print(f"Cardiac Drift:    {report.cardiac_drift_trend} bpm/(m/s)")
    print(f"Max HR Drop:      {report.max_hr_drop} bpm at Lap {report.max_hr_drop_lap}")
    print(f"EPOC:             {report.epoc} mL/kg | Hardest Lap: #{report.peak_epoc_lap}")
