import os, sys, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
FROM_EMAIL  = os.getenv("GARMIN_EMAIL")
APP_PASS    = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL    = "maxxsotelo@gmail.com"

subject = "🏃‍♂️ Antigravity Coaching | Week 14 Training Blueprint (Build II Step-Up & 24K Target)"

plain_text = """
Antigravity Coaching Telemetry & Training Blueprint
Athlete: Max Sotelo | Date: Monday, September 21, 2026
Subject: Week 14 Training Blueprint (Build II Step-Up & 24K Target)

Good afternoon Max,

Here is your full audit and Week 14 Training Blueprint (Sep 21 – Sep 27, 2026) based on your verified Garmin telemetry.

=== 1. EXHAUSTIVE TELEMETRY AUDIT (PAST 7 DAYS) ===
- Mon Sep 14: 3.00 km Treadmill Shakeout (16.6m, Avg HR 145, TE 2.2)
- Tue Sep 15: 6.29 km Treadmill (34.9m, Avg HR 155, TE 3.4, 1.3k hill climb) + 38m Heavy Pull Strength
- Wed Sep 16: 7.00 km Threshold Speed (36.2m, Avg HR 156, Max HR 186 bpm, TE 3.1/1.9) + 15.8m Strength
- Thu Sep 17: 0.00 km Running (1.04 km walking, rest day honored)
- Fri Sep 18: 6.52 km Lunch Run (34.9m, Avg HR 144, TE 2.6) + 18.6m Recumbent Spin + 88.7m Pull Strength
- Sat Sep 19: 20.07 km Rolling Hill Simulation (1:47:48, 5:22/km, Avg HR 150, Max HR 173, +179m climbed, TE 3.4) + 29.3m Arm Pump
- Sun Sep 20: 3.00 km Shakeout (17.5m, Avg HR 134, TE 2.0) + 40.9m Strength + 109m Cardio
Total Week 13 Volume: 45.88 km (Cleanly hit our 45-48 km target!)

=== 2. CORE ENGINES & CURRENT VITALS (SEP 21, 2026) ===
- Mechanical ACWR: 0.907 (Acute: 42.88 km, Chronic: 189.05 km - Optimal Sweet Spot)
- Overnight HRV: 105 ms (Balanced)
- Resting HR: 40 bpm
- Sleep Architecture: Score 79 (6.38 hours, 91 minutes Deep Sleep - 24% deep!)
- Body Battery: Recharged 68 points, sitting at 50/100 mid-afternoon.

=== 3. WEEK 14 BLUEPRINT: BUILD II STEP-UP (SEP 21 - SEP 27) ===
Target Weekly Volume: 50.0 - 52.0 km | Sunday Long Run: 24.0 km | ACWR: ~1.10

- MON SEP 21 (TODAY): Easy Shakeout (4.0 km) OR Full Rest (walking commutes logged)
- TUE SEP 22: 7.0 km Zone 2 Aerobic Cruise (162-172 bpm) + Upper Body Push & Core at AF Taft
- WED SEP 23: Quality Threshold Anchor: 8.5 km Total (2k Warmup + 5x1,000m @ 4:15-4:25/km with 90s jog + 1.5k Cooldown)
- THU SEP 24: Condo Pool Hydrotherapy Flush (35m swim/flutter kick) + Upper Body Pull Strength (0.0 km running impact)
- FRI SEP 25: 7.5 km Zone 2 Foundation Cruise + 4x100m Strides
- SAT SEP 26: 4.0 km Pre-Long Run Priming Shakeout + Carb Load
- SUN SEP 27: Build II Milestone Long Run (24.0 km Zone 2 progressive, practice 3-4 energy gels with hydration)

Full details committed to brain_current_week_plan.py.
"""

html_content = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px; }
  .container { max-width: 680px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 32px; border: 1px solid #334155; }
  h1 { color: #38bdf8; font-size: 24px; margin-bottom: 6px; }
  .subtitle { color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 24px; }
  h2 { color: #00d4aa; font-size: 16px; margin-top: 24px; border-bottom: 1px solid #334155; padding-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
  p, li { color: #cbd5e1; font-size: 14px; line-height: 1.6; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }
  .card { background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 14px; }
  .card-label { font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; }
  .card-value { font-size: 20px; font-weight: bold; color: #38bdf8; margin-top: 4px; }
  .card-sub { font-size: 12px; color: #64748b; margin-top: 2px; }
  table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }
  th { text-align: left; padding: 10px; background: #0f172a; color: #38bdf8; border-bottom: 2px solid #334155; }
  td { padding: 10px; border-bottom: 1px solid #334155; color: #cbd5e1; vertical-align: top; }
  .day-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #0369a1; color: white; margin-right: 6px; }
  .dist-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #059669; color: white; }
  .dist-rest { background: #475569; }
  .dist-quality { background: #d97706; }
  .dist-long { background: #7c3aed; }
  .footer { margin-top: 32px; font-size: 12px; color: #64748b; border-top: 1px solid #334155; padding-top: 16px; text-align: center; }
</style>
</head>
<body>
<div class="container">
  <h1>🏃‍♂️ Week 14 Training Blueprint</h1>
  <div class="subtitle">Antigravity Coaching • Build II Step-Up (Sep 21 – Sep 27, 2026)</div>

  <h2>1. Telemetry & Engine Vitals Audit</h2>
  <div class="grid">
    <div class="card">
      <div class="card-label">Mechanical ACWR</div>
      <div class="card-value">0.907</div>
      <div class="card-sub">Optimal Sweet Spot (Safe)</div>
    </div>
    <div class="card">
      <div class="card-label">Overnight HRV</div>
      <div class="card-value">105 ms</div>
      <div class="card-sub">Balanced (Baseline 101–137 ms)</div>
    </div>
    <div class="card">
      <div class="card-label">Resting Heart Rate</div>
      <div class="card-value">40 bpm</div>
      <div class="card-sub">Elite parasympathetic tone</div>
    </div>
    <div class="card">
      <div class="card-label">Deep Sleep Last Night</div>
      <div class="card-value">91 mins (24%)</div>
      <div class="card-sub">Score 79 (Complete recovery)</div>
    </div>
  </div>

  <h2>2. Week 13 Recap: 45.88 km Banked</h2>
  <p>You cleanly hit our 45–48 km target last week, highlighted by Saturday's <strong>20.07 km rolling hill simulation (+179m climbed in 1:47:48 @ 5:22/km)</strong> with an avg HR of 150 bpm.</p>

  <h2>3. Week 14 Day-by-Day Blueprint (50–52 km Target)</h2>
  <table>
    <thead>
      <tr>
        <th>Day</th>
        <th>Session & Intensity</th>
        <th style="text-align: right;">Distance</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="day-badge">MON · SEP 21</span>Today</td>
        <td><strong>Active Recovery Shakeout / Rest</strong><br>Keep HR &lt; 150 bpm at AF Taft or take full rest after 1.2k walking commutes.</td>
        <td style="text-align: right;"><span class="dist-badge">4.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">TUE · SEP 22</span>Tuesday</td>
        <td><strong>Zone 2 Aerobic Base Cruise + Upper Push</strong><br>162–172 bpm. Follow with chest, shoulders, triceps & core at AF Taft.</td>
        <td style="text-align: right;"><span class="dist-badge">7.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">WED · SEP 23</span>Wednesday</td>
        <td><strong>Quality Threshold Speed Anchor</strong><br>2k Warmup + 5x1,000m @ 4:15–4:25/km (90s jog) + 1.5k Cooldown.</td>
        <td style="text-align: right;"><span class="dist-badge dist-quality">8.5 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">THU · SEP 24</span>Thursday</td>
        <td><strong>Condo Pool Flush + Upper Pull</strong><br>35m hydrotherapy swim flush + lat pulldowns & rows. 0.0 ground reaction force.</td>
        <td style="text-align: right;"><span class="dist-badge dist-rest">0.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">FRI · SEP 25</span>Friday</td>
        <td><strong>Aerobic Foundation Cruise + Strides</strong><br>Zone 2 cruising + 4x100m relaxed strides for hip mobility and turnover.</td>
        <td style="text-align: right;"><span class="dist-badge">7.5 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">SAT · SEP 26</span>Saturday</td>
        <td><strong>Pre-Long Run Priming Shakeout</strong><br>Effortless 4k shakeout. High complex carbohydrate fueling day (rice/sweet potato).</td>
        <td style="text-align: right;"><span class="dist-badge">4.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">SUN · SEP 27</span>Sunday</td>
        <td><strong>Build II Milestone Long Run (24K)</strong><br>Cornerstone endurance anchor. Practice in-run fueling (3–4 gels at Km 7, 13, 18).</td>
        <td style="text-align: right;"><span class="dist-badge dist-long">24.0 km</span></td>
      </tr>
    </tbody>
  </table>

  <p style="margin-top: 16px; font-size: 13px;">
    <strong>Projected Volume:</strong> <strong>~51.0 km</strong> · <strong>Projected ACWR:</strong> <strong>~1.10</strong> (Optimal Sweet Spot).
  </p>

  <div class="footer">
    Antigravity AI Coaching System • Generated for Max Sotelo • Bangko Sentral ng Pilipinas & AF Taft Edition
  </div>
</div>
</body>
</html>
"""

def send():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Antigravity Coach <{FROM_EMAIL}>"
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(FROM_EMAIL, APP_PASS)
        server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
    print(f"[OK] Successfully emailed Week 14 Blueprint to {TO_EMAIL}!")

if __name__ == "__main__":
    send()
