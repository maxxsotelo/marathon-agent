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

subject = "🏃‍♂️ Antigravity Coaching | Week 14 Audit & Calf Recovery Protocol"

plain_text = """
Antigravity Coaching Telemetry & Training Audit
Athlete: Max Sotelo | Date: Thursday, September 24, 2026
Subject: Week 14 Mid-Week Audit & Right Calf Recovery Protocol

Good morning Max,

Here is your full mid-week telemetry audit and adjusted roadmap following your Wednesday calf tightness.

=== 1. MID-WEEK TELEMETRY AUDIT (SEP 21 - SEP 24) ===
- Mon Sep 21: 1.40 km Shakeout Run (Avg HR 127, TE 0.8) + 18m Cardio + 2.16 km Walking
- Tue Sep 22: 7.00 km Treadmill @ 1-2.5% Incline (37.2m, Avg HR 150, Max HR 165, TE 2.9) + 46m Upper Push & Core
- Wed Sep 23: 3.50 km Treadmill (20.3m, Avg HR 136, Max HR 148, TE 2.0) + 9.3m Spin + 2.45 km Walking
  * Tactical Note: Calves tightened up; you aborted the 5x1k speed session after 3.5k easy jogging. Elite decision!
Total Running Banked (Mon-Wed): 11.99 km (~12.0 km)
Mechanical ACWR: 0.882 (Safe Sweet Spot: 41.58 km acute / 188.61 km chronic)

=== 2. ROOT-CAUSE ANALYSIS OF RIGHT CALF TIGHTNESS ===
1. Double-Incline Loading: Saturday's 20.07 km rolling hill simulation (+179m climbed) followed 72 hours later by Tuesday's 7.00 km at 1-2.5% incline overloaded the gastrocnemius-soleus complex.
2. Concrete Commuting: 6.7 km of walking on hard pavement in street shoes between condo, BSP, and AF Taft added unmonitored ground reaction force.
3. Nocturnal Cramp: Points to electrolyte shift (magnesium/sodium) exacerbated by tropical heat and air-conditioned sleep.

=== 3. ADJUSTED WEEK 14 ROADMAP (CALF RECOVERY) ===
- THU SEP 24 (TODAY): 0.0 KM RUNNING IMPACT
  * Primary: W14D4 Condo Pool Flush [35m] (Garmin ID: 1705207018) - Hydrostatic pressure flushes calf micro-edema with 0 ground shock.
  * Strength: W14D4 Upper Pull & Core (Garmin ID: 1705207056) - Lat pulldowns, rows, face pulls. Strict veto on legs.
  * Rehab: 400mg Magnesium tonight, add electrolytes to water, gentle straight/bent-knee wall calf stretches.

- FRI SEP 25: 5.0 - 6.0 KM FLAT AEROBIC CRUISE
  * Treadmill at 0.0% or 0.5% incline (NO HILLS). HR strictly < 155 bpm.
  * VETO: Strides cancelled to eliminate high eccentric toe-off strain. Shoes: Puma Velocity Nitro 3.

- SAT SEP 26: 4.0 KM PRE-LONG RUN SHAKEOUT & CARB LOAD
  * Effortless 4 km shakeout (or full rest if calf is still sensitive). Carb load with extra rice, sweet potatoes, and sodium.

- SUN SEP 27: 20.0 - 22.0 KM BUILD II MILESTONE LONG RUN
  * Adjusted down from 24k to 20-22k flat Zone 2 cruise. Full race fueling practice (3 gels at Km 7, 13, 18).

All workouts are already synchronized directly to your Garmin watch calendar.
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
  <h1>🏃‍♂️ Week 14 Audit & Calf Recovery Protocol</h1>
  <div class="subtitle">Antigravity Coaching • Build II Calibration (Sep 21 – Sep 27, 2026)</div>

  <div class="alert-box">
    <strong>Tactical Commendation:</strong> Bailing on Wednesday's 5x1,000m speed repeats after 3.5k easy jogging when your calf tightened was an <strong>elite coaching decision</strong>. Forcing threshold intervals on a spasming calf is the #1 way runners tear their soleus or Achilles.
  </div>

  <h2>1. Telemetry & Engine Vitals</h2>
  <div class="grid">
    <div class="card">
      <div class="card-label">Mechanical ACWR</div>
      <div class="card-value">0.882</div>
      <div class="card-sub">Optimal Sweet Spot (Safe)</div>
    </div>
    <div class="card">
      <div class="card-label">Overnight HRV</div>
      <div class="card-value">114–121 ms</div>
      <div class="card-sub">Balanced (Strong Recovery)</div>
    </div>
    <div class="card">
      <div class="card-label">Resting Heart Rate</div>
      <div class="card-value">38–40 bpm</div>
      <div class="card-sub">Elite parasympathetic tone</div>
    </div>
    <div class="card">
      <div class="card-label">Volume Banked (Mon–Wed)</div>
      <div class="card-value">11.99 km</div>
      <div class="card-sub">Mon 1.4k + Tue 7k + Wed 3.5k</div>
    </div>
  </div>

  <h2>2. Root-Cause: The Double-Incline Mechanism</h2>
  <ul>
    <li><strong>Saturday Sep 19:</strong> 20.07 km Rolling Hill simulation (+179m climbed) shifted heavy mechanical load to the gastrocnemius/soleus.</li>
    <li><strong>Tuesday Sep 22:</strong> 7.00 km at 1.0–2.5% treadmill incline re-loaded calves before deep eccentric remodeling was complete.</li>
    <li><strong>Concrete Impact:</strong> 6.7 km of walking in street shoes across Manila sidewalks added sustained micro-shocks.</li>
    <li><strong>Nocturnal Cramp:</strong> Points to electrolyte depletion (magnesium/sodium) in tropical humidity + air-conditioned sleep.</li>
  </ul>

  <h2>3. Adjusted Plan for Rest of Week 14</h2>
  <table>
    <thead>
      <tr>
        <th>Day</th>
        <th>Adjusted Session</th>
        <th style="text-align: right;">Distance</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><span class="day-badge">THU · SEP 24</span>Today</td>
        <td><strong>Condo Pool Flush + Upper Pull (0.0 km Run)</strong><br>35m hydrotherapy swim flush (Garmin ID: 1705207018) + lat pulldowns & rows. Zero ground impact.</td>
        <td style="text-align: right;"><span class="dist-badge dist-rest">0.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">FRI · SEP 25</span>Friday</td>
        <td><strong>Flat Aerobic Base Cruise (Strides Vetoed)</strong><br>5.0–6.0 km flat treadmill (0.0% or 0.5% incline, NO HILLS) @ &lt;155 bpm. Strides canceled to eliminate toe-off strain.</td>
        <td style="text-align: right;"><span class="dist-badge">5.5 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">SAT · SEP 26</span>Saturday</td>
        <td><strong>Pre-Long Run Priming Shakeout</strong><br>Easy 4.0 km shakeout (<148 bpm). High complex carb & sodium fueling day.</td>
        <td style="text-align: right;"><span class="dist-badge">4.0 km</span></td>
      </tr>
      <tr>
        <td><span class="day-badge">SUN · SEP 27</span>Sunday</td>
        <td><strong>Build II Long Run Calibration (20–22 km)</strong><br>Adjusted down from 24k to 20–22k flat Zone 2 cruise. Full race fueling practice (3 gels at Km 7, 13, 18).</td>
        <td style="text-align: right;"><span class="dist-badge dist-long">21.0 km</span></td>
      </tr>
    </tbody>
  </table>

  <h2>4. Calf Recovery Protocol</h2>
  <ol>
    <li><strong>Electrolytes & Hydration:</strong> Take 400 mg Magnesium glycinate tonight. Add electrolyte powder/sodium to your water bottle today.</li>
    <li><strong>Hydrostatic Pool Flush:</strong> Today's 35m pool swim compresses the lower leg to rapidly flush micro-edema without joint impact.</li>
    <li><strong>Soft Tissue & Stretches:</strong> Foam roll the meaty belly of the calf/soleus (avoid the Achilles). 30s straight-knee and 30s bent-knee wall calf stretches.</li>
  </ol>

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
    print(f"[OK] Successfully emailed Week 14 Audit & Calf Protocol to {TO_EMAIL}!")

if __name__ == "__main__":
    send()
