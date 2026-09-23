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

subject = "🏃‍♂️ Antigravity Coaching | Saturday Long Run Blueprint & Marikina Adjustments"

plain_text = """
Antigravity Coaching Telemetry & Schedule Reorganization
Athlete: Max Sotelo | Date: Thursday, September 24, 2026
Subject: Saturday Long Run Blueprint & Marikina Logistics

Hey Max,

Your calendar and training blueprint have been completely reorganized and synced to your Garmin watch:

=== 1. MARIKINA & SATURDAY LONG RUN ADJUSTMENTS ===
- Thursday (Today): Heading home to Marikina. Swim session cancelled! Replaced with 35m light indoor bike flush (Garmin ID: 1707881479) + Upper Pull & Core (Garmin ID: 1705207056). 0.0 km running impact.
- Friday Sep 25: Pre-Long Run Priming Shakeout (4.0 km easy flat cruise, HR < 148 bpm) in Puma Velocity Nitro 3s + High-carb fueling. (Old strides and 5.5k sessions removed).
- Saturday Sep 26: Build II Milestone Long Run (20.0 – 22.0 km flat Zone 2 cruise, 162–172 bpm) in Marikina (flat roads / riverbanks / treadmill). Fueling practice with 3 gels at Km 7, 13, 18.
- Sunday Sep 27: Post-Long Run Active Recovery Flush (3.5 – 4.0 km easy recovery jog <145 bpm or 30m spin / full rest).

=== 2. TREADMILL CONTENTION / BIKE FLUSH PROTOCOL ===
Your smart adaptation on Monday (18m bike) and Wednesday (9.3m bike) when treadmills were occupied is officially incorporated into your training lore.
Riding the stationary bike at low resistance (Zone 1, <125 bpm) while waiting for a treadmill counts towards active aerobic volume with 0.0 ground reaction force!

All workouts are updated on your Garmin Connect calendar.
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
  .alert-box { background-color: #172554; border-left: 4px solid #38bdf8; padding: 14px; border-radius: 6px; margin: 16px 0; font-size: 13px; color: #bae6fd; }
  table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 13px; }
  th { text-align: left; padding: 10px; background: #0f172a; color: #38bdf8; border-bottom: 2px solid #334155; }
  td { padding: 10px; border-bottom: 1px solid #334155; color: #cbd5e1; vertical-align: top; }
  .day-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #0369a1; color: white; margin-right: 6px; }
  .dist-badge { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #059669; color: white; }
  .dist-rest { background: #475569; }
  .dist-long { background: #7c3aed; }
  .footer { margin-top: 32px; font-size: 12px; color: #64748b; border-top: 1px solid #334155; padding-top: 16px; text-align: center; }
</style>
</head>
<body>
<div class="container">
  <h1>🏃‍♂️ Saturday Long Run Blueprint</h1>
  <div class="subtitle">Antigravity Coaching • Marikina Weekend Reorganization (Sep 24 – Sep 27, 2026)</div>

  <div class="alert-box">
    <strong>Schedule Shift Confirmed:</strong> Long Run moved to <strong>Saturday, Sep 26 (21 km)</strong>. Thursday swims permanently decommissioned for Marikina days and replaced with stationary bike flushing.
  </div>

  <h2>1. Updated Weekend Calendar (Synced to Garmin)</h2>
  <table>
    <thead>
      <tr>
        <th>Day</th>
        <th>Session & Protocol</th>
        <th style="text-align: right;">Volume</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="day-badge">THU · SEP 24</span>Today</td>
        <td><strong>Marikina Indoor Bike Flush + Upper Pull</strong><br>35m light spinning (&lt;125 bpm, Garmin ID: 1707881479) + lat pulldowns & rows. Zero ground reaction force.</td>
        <td style="text-align: right;"><span class="dist-badge dist-rest">0.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">FRI · SEP 25</span>Tomorrow</td>
        <td><strong>Pre-Long Run Priming Shakeout (4K)</strong><br>Easy 4.0 km flat cruise (&lt;148 bpm, Garmin ID: 1707881487). Keep legs completely fresh. Carb-load today!</td>
        <td style="text-align: right;"><span class="dist-badge">4.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">SAT · SEP 26</span>Saturday</td>
        <td><strong>Build II Milestone Long Run (21K)</strong><br>20.0–22.0 km flat Zone 2 cruise (162–172 bpm, Garmin ID: 1707881493). In-run fueling: 3 gels at Km 7, 13, 18.</td>
        <td style="text-align: right;"><span class="dist-badge dist-long">21.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">SUN · SEP 27</span>Sunday</td>
        <td><strong>Post-Long Run Active Recovery Flush</strong><br>3.5–4.0 km very easy recovery jog (&lt;145 bpm, Garmin ID: 1707881496) or 30m easy spin / rest.</td>
        <td style="text-align: right;"><span class="dist-badge">4.0 km</span></td>
      </tr>
    </tbody>
  </table>

  <h2>2. Treadmill Contention & Indoor Bike Protocol</h2>
  <p>Hopping on the stationary bike instead of standing idle during gym rush hours (Monday 18m, Wednesday 9.3m) is an <strong>elite active recovery adaptation</strong>:</p>
  <ul>
    <li>It keeps your core temperature elevated and promotes concentric blood circulation to the calves/quads without ground impact.</li>
    <li>Moving forward: When treadmills are occupied, 10–20 mins of light spinning (&lt;125 bpm) is officially sanctioned as a warmup or active flush!</li>
  </ul>

  <h2>3. Calf Protection for Saturday's 21K</h2>
  <ul>
    <li><strong>Flat Course Only:</strong> Run your 21k on flat surfaces (Marikina Riverbanks flat sections or flat road/treadmill). Avoid steep bridge/hill repeats.</li>
    <li><strong>Shoes:</strong> Lace up your <strong>Puma Velocity Nitro 3</strong> (generous 10mm heel drop insulates Achilles & soleus).</li>
    <li><strong>Fueling & Hydration:</strong> 400mg Magnesium tonight, extra hydration Friday, and 3 energy gels with water during Saturday's run.</li>
  </ul>

  <div class="footer">
    Antigravity AI Coaching System • Generated for Max Sotelo • Marikina Weekend Edition
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
    print(f"[OK] Successfully emailed Saturday Long Run Blueprint to {TO_EMAIL}!")

if __name__ == "__main__":
    send()
