"""
biometrics_trend.py
===================
Fetches 30 days of biometric data from Garmin Connect and renders a
multi-panel trend chart covering:
  • Resting Heart Rate (bpm)
  • HRV — Last Night & 7-day Rolling Average (ms)
  • Body Battery (end-of-day peak)
  • Stress Score (daily average)
  • Sleep — Total duration + stage breakdown (Deep / REM)
  • Weight (kg)

Usage:
  python biometrics_trend.py              # renders + saves biometrics_trend.png
  python biometrics_trend.py --days 14   # override lookback window
  python biometrics_trend.py --show      # open interactive matplotlib window
"""

import os
import sys
import argparse
from datetime import date, timedelta
from dotenv import load_dotenv

import matplotlib
matplotlib.use("Agg")  # headless by default; --show overrides
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import numpy as np

load_dotenv()

# ── Garmin client setup ──────────────────────────────────────────────────────
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")

def get_client():
    client = Garmin(
        email=os.getenv("GARMIN_EMAIL"),
        password=os.getenv("GARMIN_PASSWORD"),
        prompt_mfa=lambda: input("Garmin MFA code: "),
    )
    client.login(TOKEN_STORE)
    return client


# ── Data collection ──────────────────────────────────────────────────────────
def fetch_range(client, days: int) -> list[dict]:
    """
    Iterate over the last `days` dates and collect biometric snapshots.
    Returns a list of dicts, one per date, sorted ascending.
    """
    today = date.today()
    rows = []

    for offset in range(days - 1, -1, -1):   # oldest → newest
        d = today - timedelta(days=offset)
        iso = d.isoformat()
        row = {"date": d}

        # ── User summary (RHR, Body Battery, Stress, Steps) ─────────────────
        try:
            summary = client.get_user_summary(iso)
            row["rhr"]          = summary.get("restingHeartRate")
            row["body_battery"] = summary.get("bodyBatteryMostRecentValue")
            row["stress"]       = summary.get("averageStressLevel")
            row["steps"]        = summary.get("totalSteps")
            row["active_kcal"]  = summary.get("activeKilocalories")
            row["total_kcal"]   = summary.get("totalKilocalories")
        except Exception:
            row.update({"rhr": None, "body_battery": None, "stress": None,
                        "steps": None, "active_kcal": None, "total_kcal": None})

        # ── Sleep ────────────────────────────────────────────────────────────
        try:
            sleep = client.get_sleep_data(iso)
            dto = sleep.get("dailySleepDTO", {})
            total = (dto.get("sleepTimeInSeconds")
                     or dto.get("totalSleepSeconds") or 0)
            deep  = (dto.get("deepSleepSeconds")
                     or dto.get("deepSleepDurationInSeconds") or 0)
            rem   = (dto.get("remSleepSeconds")
                     or dto.get("remSleepInSeconds") or 0)
            row["sleep_total_h"] = total / 3600 if total else None
            row["sleep_deep_h"]  = deep  / 3600 if deep  else None
            row["sleep_rem_h"]   = rem   / 3600 if rem   else None
            row["sleep_score"]   = dto.get("sleepScore")
        except Exception:
            row.update({"sleep_total_h": None, "sleep_deep_h": None,
                        "sleep_rem_h": None,   "sleep_score": None})

        # ── HRV ──────────────────────────────────────────────────────────────
        try:
            hrv = client.get_hrv_data(iso)
            if hrv and "hrvSummary" in hrv:
                row["hrv_last"]  = hrv["hrvSummary"].get("lastNightAvg")
                row["hrv_7d"]    = hrv["hrvSummary"].get("weeklyAvg")
                row["hrv_5min"]  = hrv["hrvSummary"].get("lastNight5MinHigh")
            else:
                row.update({"hrv_last": None, "hrv_7d": None, "hrv_5min": None})
        except Exception:
            row.update({"hrv_last": None, "hrv_7d": None, "hrv_5min": None})

        # ── Weight ───────────────────────────────────────────────────────────
        try:
            body = client.get_body_composition(iso)
            w = body.get("totalWeight")
            row["weight"] = w / 1000 if w and w > 100 else w  # grams → kg
        except Exception:
            row["weight"] = None

        rows.append(row)
        print(f"  [{iso}] RHR={row['rhr']} HRV={row['hrv_last']} "
              f"BB={row['body_battery']} Stress={row['stress']} "
              f"Sleep={row['sleep_total_h']:.1f}h" if row['sleep_total_h'] else
              f"  [{iso}] RHR={row['rhr']} HRV={row['hrv_last']} "
              f"BB={row['body_battery']} Stress={row['stress']} Sleep=N/A")

    return rows


# ── Helpers ──────────────────────────────────────────────────────────────────
def _vals(rows, key):
    """Return (dates, values) with Nones preserved for plotting gaps."""
    dates = [r["date"] for r in rows]
    vals  = [r.get(key) for r in rows]
    return dates, vals

def _masked(vals):
    """Convert list-with-Nones to a numpy masked array for clean line plots."""
    arr = np.array([v if v is not None else np.nan for v in vals], dtype=float)
    return np.ma.masked_invalid(arr)

def _rolling_avg(vals, window=7):
    arr = _masked(vals)
    out = np.full_like(arr, np.nan)
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        chunk = arr[start : i + 1]
        valid = chunk[~np.ma.getmaskarray(chunk)]
        if len(valid):
            out[i] = float(valid.mean())
    return out

def _trend_line(dates, vals):
    """Linear regression trend — returns (x_fit, y_fit) or None."""
    x = np.array([d.toordinal() for d in dates])
    y = np.array([v if v is not None else np.nan for v in vals], dtype=float)
    mask = ~np.isnan(y)
    if mask.sum() < 3:
        return None, None
    m, b = np.polyfit(x[mask], y[mask], 1)
    x_fit = np.array([x[mask][0], x[mask][-1]])
    y_fit = m * x_fit + b
    dates_fit = [date.fromordinal(int(xv)) for xv in x_fit]
    return dates_fit, y_fit, m


# ── Chart ────────────────────────────────────────────────────────────────────
DARK_BG   = "#0f1117"
PANEL_BG  = "#1a1d27"
GRID_COL  = "#2a2d3a"
TEXT_COL  = "#e0e0e0"
ACCENT    = "#7c83fd"   # indigo
GREEN     = "#3ddc84"
ORANGE    = "#ffa657"
RED       = "#ff6b6b"
CYAN      = "#56d0e0"
YELLOW    = "#f7c948"
PURPLE    = "#c678dd"

def make_chart(rows: list[dict], out_path: str, show: bool = False):
    dates = [r["date"] for r in rows]
    n = len(rows)

    fig = plt.figure(figsize=(18, 22), facecolor=DARK_BG)
    fig.suptitle(
        f"Max · Biometric Trend Dashboard  ({dates[0].strftime('%b %d')} – {dates[-1].strftime('%b %d, %Y')})",
        fontsize=16, fontweight="bold", color=TEXT_COL, y=0.98
    )

    # 6 rows × 1 col, shared x axis
    axes = []
    for idx in range(6):
        if idx == 0:
            ax = fig.add_subplot(6, 1, 1)
        else:
            ax = fig.add_subplot(6, 1, idx + 1, sharex=axes[0])
        ax.set_facecolor(PANEL_BG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COL)
        ax.tick_params(colors=TEXT_COL, which="both")
        ax.yaxis.label.set_color(TEXT_COL)
        ax.grid(axis="y", color=GRID_COL, linewidth=0.6, alpha=0.7)
        ax.grid(axis="x", color=GRID_COL, linewidth=0.3, alpha=0.4)
        axes.append(ax)

    # ── Panel 0: Resting Heart Rate ──────────────────────────────────────────
    ax = axes[0]
    _, rhr = _vals(rows, "rhr")
    rhr_m = _masked(rhr)
    rhr_roll = _rolling_avg(rhr, 7)
    ax.plot(dates, rhr_m, color=RED, linewidth=1.5, alpha=0.6, marker="o",
            markersize=3, label="RHR (nightly)")
    ax.plot(dates, rhr_roll, color=ORANGE, linewidth=2.2, label="7d Rolling Avg")
    # trend
    tf = _trend_line(dates, rhr)
    if tf[0]:
        ax.plot(tf[0], tf[1], "--", color=ORANGE, linewidth=1, alpha=0.5)
    ax.set_ylabel("bpm", fontsize=9)
    ax.set_title("Resting Heart Rate", fontsize=10, color=TEXT_COL, loc="left", pad=4)
    ax.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXT_COL, loc="upper right")
    # annotate current value
    last_rhr = next((v for v in reversed(rhr) if v is not None), None)
    if last_rhr:
        ax.annotate(f"{last_rhr:.0f} bpm", xy=(dates[-1], last_rhr),
                    xytext=(5, 0), textcoords="offset points",
                    fontsize=8, color=RED)

    # ── Panel 1: HRV ────────────────────────────────────────────────────────
    ax = axes[1]
    _, hrv_last = _vals(rows, "hrv_last")
    _, hrv_7d   = _vals(rows, "hrv_7d")
    hrv_last_m  = _masked(hrv_last)
    hrv_7d_m    = _masked(hrv_7d)
    ax.fill_between(dates, hrv_last_m, alpha=0.15, color=CYAN)
    ax.plot(dates, hrv_last_m, color=CYAN, linewidth=1.5, alpha=0.7,
            marker="o", markersize=3, label="Last Night HRV")
    ax.plot(dates, hrv_7d_m,   color=ACCENT, linewidth=2.4, label="7d Avg HRV")
    tf = _trend_line(dates, hrv_last)
    if tf[0]:
        direction = "↑ Trending up" if tf[2] > 0 else "↓ Trending down"
        ax.plot(tf[0], tf[1], "--", color=ACCENT, linewidth=1, alpha=0.5)
        ax.text(0.02, 0.05, direction, transform=ax.transAxes,
                fontsize=8, color=ACCENT, alpha=0.85)
    ax.set_ylabel("ms", fontsize=9)
    ax.set_title("Heart Rate Variability (HRV)", fontsize=10, color=TEXT_COL, loc="left", pad=4)
    ax.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXT_COL, loc="upper right")

    # ── Panel 2: Body Battery ────────────────────────────────────────────────
    ax = axes[2]
    _, bb = _vals(rows, "body_battery")
    bb_m = _masked(bb)
    # colour code zones
    for i in range(n - 1):
        if bb[i] is not None and bb[i+1] is not None:
            seg_avg = (bb[i] + bb[i+1]) / 2
            col = (GREEN if seg_avg >= 75 else
                   YELLOW if seg_avg >= 50 else
                   ORANGE if seg_avg >= 25 else RED)
            ax.fill_between([dates[i], dates[i+1]], [bb[i], bb[i+1]], alpha=0.25, color=col)
            ax.plot([dates[i], dates[i+1]], [bb[i], bb[i+1]], color=col, linewidth=2)
    ax.axhline(50, color=YELLOW, linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhline(25, color=RED,    linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_ylim(0, 100)
    ax.set_ylabel("/ 100", fontsize=9)
    ax.set_title("Body Battery (End-of-Day)", fontsize=10, color=TEXT_COL, loc="left", pad=4)
    legend_els = [
        mpatches.Patch(color=GREEN,  label="High (75–100)"),
        mpatches.Patch(color=YELLOW, label="Moderate (50–74)"),
        mpatches.Patch(color=ORANGE, label="Low (25–49)"),
        mpatches.Patch(color=RED,    label="Drained (0–24)"),
    ]
    ax.legend(handles=legend_els, fontsize=7, facecolor=PANEL_BG,
              labelcolor=TEXT_COL, loc="upper right", ncol=2)

    # ── Panel 3: Stress ──────────────────────────────────────────────────────
    ax = axes[3]
    _, stress = _vals(rows, "stress")
    stress_m = _masked(stress)
    stress_roll = _rolling_avg(stress, 7)
    ax.bar(dates, stress_m, color=PURPLE, alpha=0.4, width=0.7)
    ax.plot(dates, stress_roll, color=PURPLE, linewidth=2.2, label="7d Rolling Avg")
    ax.axhline(25, color=GREEN,  linewidth=0.7, linestyle="--", alpha=0.5, label="Low stress")
    ax.axhline(50, color=ORANGE, linewidth=0.7, linestyle="--", alpha=0.5, label="High stress")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Score", fontsize=9)
    ax.set_title("Daily Average Stress", fontsize=10, color=TEXT_COL, loc="left", pad=4)
    ax.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXT_COL, loc="upper right")

    # ── Panel 4: Sleep ──────────────────────────────────────────────────────
    ax = axes[4]
    _, sleep_tot  = _vals(rows, "sleep_total_h")
    _, sleep_deep = _vals(rows, "sleep_deep_h")
    _, sleep_rem  = _vals(rows, "sleep_rem_h")
    sleep_tot_m  = _masked(sleep_tot)
    sleep_deep_m = _masked(sleep_deep)
    sleep_rem_m  = _masked(sleep_rem)

    ax.fill_between(dates, sleep_tot_m,  alpha=0.15, color=ACCENT, label="Total Sleep")
    ax.plot(dates, sleep_tot_m,  color=ACCENT,  linewidth=2,   label="_nolegend_")
    ax.fill_between(dates, sleep_deep_m, alpha=0.35, color=CYAN)
    ax.plot(dates, sleep_deep_m, color=CYAN,    linewidth=1.5, label="Deep Sleep")
    ax.fill_between(dates, sleep_rem_m,  alpha=0.25, color=GREEN)
    ax.plot(dates, sleep_rem_m,  color=GREEN,   linewidth=1.5, label="REM Sleep")
    ax.axhline(7, color=YELLOW, linewidth=0.8, linestyle="--", alpha=0.6, label="Target 7h")
    ax.axhline(1.5, color=CYAN, linewidth=0.6, linestyle=":", alpha=0.5, label="Target Deep 1.5h")
    ax.set_ylabel("Hours", fontsize=9)
    ax.set_title("Sleep (Total / Deep / REM)", fontsize=10, color=TEXT_COL, loc="left", pad=4)
    ax.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXT_COL, loc="upper right", ncol=2)

    # ── Panel 5: Weight ──────────────────────────────────────────────────────
    ax = axes[5]
    _, weight = _vals(rows, "weight")
    weight_m = _masked(weight)
    # forward-fill weight for projection (Garmin only logs on weigh-in days)
    weight_ff = []
    last_w = None
    for w in weight:
        if w is not None:
            last_w = w
        weight_ff.append(last_w)
    weight_ff_m = _masked(weight_ff)

    ax.plot(dates, weight_ff_m, color=YELLOW, linewidth=2, label="Weight (kg)", marker="o", markersize=3)
    # 70kg target line
    ax.axhline(70, color=GREEN, linewidth=1.2, linestyle="--", alpha=0.7, label="Target 70 kg")
    tf = _trend_line(dates, weight_ff)
    if tf[0]:
        ax.plot(tf[0], tf[1], "--", color=YELLOW, linewidth=1, alpha=0.6, label="Trend")
        # Extrapolate to 70 kg
        m_slope = tf[2]
        if m_slope and m_slope < 0:
            last_w_val  = next((v for v in reversed(weight_ff) if v is not None), None)
            if last_w_val and last_w_val > 70:
                days_to_70 = int((70 - last_w_val) / (m_slope))
                target_d   = dates[-1] + timedelta(days=days_to_70)
                ax.annotate(
                    f"70 kg by ~{target_d.strftime('%b %d')}",
                    xy=(target_d, 70), xytext=(-60, 10),
                    textcoords="offset points", fontsize=8, color=GREEN,
                    arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8)
                )
    ax.set_ylabel("kg", fontsize=9)
    ax.set_title("Body Weight", fontsize=10, color=TEXT_COL, loc="left", pad=4)
    ax.legend(fontsize=8, facecolor=PANEL_BG, labelcolor=TEXT_COL, loc="upper right")

    # ── Shared x-axis formatting ─────────────────────────────────────────────
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right",
                 color=TEXT_COL, fontsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.97], h_pad=1.8)
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    print(f"\n[OK] Chart saved → {out_path}")

    if show:
        matplotlib.use("TkAgg")
        plt.show()

    plt.close(fig)


# ── Summary stats ────────────────────────────────────────────────────────────
def print_summary(rows):
    def avg(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        return sum(vals) / len(vals) if vals else None

    def trend_label(key):
        vals = [r[key] for r in rows if r.get(key) is not None]
        if len(vals) < 4:
            return "insufficient data"
        first_half = sum(vals[:len(vals)//2]) / (len(vals)//2)
        second_half = sum(vals[len(vals)//2:]) / (len(vals) - len(vals)//2)
        delta = second_half - first_half
        if abs(delta) < 1:
            return "stable"
        return f"{'↑' if delta > 0 else '↓'} {abs(delta):.1f} avg"

    SEP = "-" * 55
    print("\n" + SEP)
    print("  BIOMETRIC TREND SUMMARY")
    print(SEP)
    a = avg("rhr");       print(f"  Avg RHR          : {a:.0f} bpm  [{trend_label('rhr')}]" if a else "  Avg RHR          : N/A")
    a = avg("hrv_last");  print(f"  Avg HRV (nightly): {a:.0f} ms   [{trend_label('hrv_last')}]" if a else "  Avg HRV          : N/A")
    a = avg("body_battery"); print(f"  Avg Body Battery : {a:.0f}/100 [{trend_label('body_battery')}]" if a else "  Avg Body Bat.     : N/A")
    a = avg("stress");    print(f"  Avg Stress       : {a:.0f}     [{trend_label('stress')}]" if a else "  Avg Stress        : N/A")
    a = avg("sleep_total_h"); print(f"  Avg Sleep        : {a:.1f}h    [{trend_label('sleep_total_h')}]" if a else "  Avg Sleep         : N/A")
    a = avg("sleep_deep_h");  print(f"  Avg Deep Sleep   : {a:.2f}h   [{trend_label('sleep_deep_h')}]" if a else "  Avg Deep Sleep    : N/A")
    a = avg("sleep_rem_h");   print(f"  Avg REM Sleep    : {a:.2f}h" if a else "  Avg REM Sleep     : N/A")

    # Weight change
    w_vals = [r["weight"] for r in rows if r.get("weight") is not None]
    if len(w_vals) >= 2:
        delta = w_vals[-1] - w_vals[0]
        print(f"  Weight Change    : {delta:+.1f} kg over period")
    print(SEP)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    # Force UTF-8 output on Windows to avoid cp1252 codec errors
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Garmin biometrics trend chart")
    parser.add_argument("--days", type=int, default=30, help="Lookback window in days (default: 30)")
    parser.add_argument("--show", action="store_true", help="Open interactive chart window")
    parser.add_argument("--out",  type=str, default="biometrics_trend.png", help="Output file path")
    args = parser.parse_args()

    print(f"Fetching {args.days} days of biometric data from Garmin Connect...")
    client = get_client()
    rows   = fetch_range(client, args.days)
    print_summary(rows)
    make_chart(rows, args.out, show=args.show)


if __name__ == "__main__":
    main()
