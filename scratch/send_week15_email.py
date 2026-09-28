import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")

email_user = os.getenv("GMAIL_USER", "maxxsotelo@gmail.com")
email_pass = os.getenv("GMAIL_APP_PASSWORD", "vkspvprfuowcrnsn")
recipient = "maxxsotelo@gmail.com"

subject = "⚡ Marathon Agent: Week 15 Blueprint (Cutback 38-40km) & 21K+ Milestone Audit"

html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
  .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
  h1 { color: #58a6ff; font-size: 24px; margin-top: 0; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
  h2 { color: #79c0ff; font-size: 18px; margin-top: 15px; }
  h3 { color: #d2a8ff; font-size: 16px; }
  .badge { background-color: #238636; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
  .badge-warn { background-color: #d29922; color: #161b22; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
  .badge-blue { background-color: #1f6feb; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
  table { width: 100%; border-collapse: collapse; margin-top: 10px; }
  th, td { border: 1px solid #30363d; padding: 10px; text-align: left; }
  th { background-color: #21262d; color: #8b949e; }
  tr:nth-child(even) { background-color: #161b22; }
  tr:nth-child(odd) { background-color: #0d1117; }
  ul { padding-left: 20px; }
  li { margin-bottom: 6px; }
  .highlight { color: #3fb950; font-weight: bold; }
</style>
</head>
<body>

<div classcard>
  <h1>🏃‍♂️ Marathon Agent — Week 15 Active Recovery Cutback Blueprint</h1>
  <p><span class="badge">VO2 MAX 59 ML/KG/MIN (ALL-TIME HIGH)</span> <span class="badge-blue">21K HM PB MATCH: 1H 48M</span> <span class="badge-warn">CUTBACK WEEK (38-40 KM)</span></p>
  <p>Hey Max, here is your officially confirmed <strong>Week 15 Schedule (Sep 28 – Oct 4, 2026)</strong>. All 8 structured workouts have been built and scheduled directly into your <strong>Garmin Connect Calendar</strong>!</p>
</div>

<div class="card">
  <h2>🎉 Breakthrough Performance Audit (Week 14 Capstone)</h2>
  <ul>
    <li><strong>VO2 Max Milestone:</strong> Reached <span class="highlight">59 ml/kg/min</span> on your Garmin FR165 following Sunday's 21.0 km heat run.</li>
    <li><strong>21K Half Marathon PB Match:</strong> 1h 48m (~5:08/km pace) executed in <strong>Adidas Adizero EVO SLs</strong> under high heat index. Equal to your previous track PB set in Boston 12s, proving massive aerobic engine growth!</li>
    <li><strong>Leg Status & Soreness:</strong> Legs are deeply sore post-run. Per your request, the 30 km long run is <strong>deferred to Week 16 (Oct 11)</strong>. Week 15 is locked as an <strong>Active Recovery Cutback (38–40 km total volume)</strong> to allow full neuromuscular & tendon remodeling.</li>
  </ul>
</div>

<div class="card">
  <h2>📊 Comprehensive 20K / 21K+ Distance Run Audit</h2>
  <p>Here is your complete historical log of 20K+ and 21K+ completed runs in the training system:</p>
  <table>
    <thead>
      <tr>
        <th>Date</th>
        <th>Distance</th>
        <th>Duration / Pace</th>
        <th>Notes / Shoe Model</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>2026-09-27</td>
        <td><span class="highlight">21.05 km</span></td>
        <td>1h 48m 12s (5:08/km)</td>
        <td><strong>Matched 21K PB in Heat!</strong> VO2 Max hit 59. Adidas EVO SL.</td>
      </tr>
      <tr>
        <td>2026-09-06</td>
        <td><span class="highlight">25.04 km</span></td>
        <td>2h 17m 45s (5:30/km)</td>
        <td>Longest block run so far. Boston 12. Perfect hydration protocol.</td>
      </tr>
      <tr>
        <td>2026-08-23</td>
        <td><span class="highlight">30.39 km</span></td>
        <td>2h 45m 18s (5:26/km)</td>
        <td><strong>Career Longest Distance Baseline.</strong> High endurance threshold.</td>
      </tr>
      <tr>
        <td>2026-08-09</td>
        <td><span class="highlight">30.00 km</span></td>
        <td>2h 42m 10s (5:24/km)</td>
        <td>Career 30K Baseline #1. High heat endurance test.</td>
      </tr>
      <tr>
        <td>2026-07-27</td>
        <td><span class="highlight">21.10 km</span></td>
        <td>1h 48m 10s (5:07/km)</td>
        <td>Track 21K HM PB baseline (Boston 12).</td>
      </tr>
      <tr>
        <td>2026-07-13</td>
        <td><span class="highlight">21.00 km</span></td>
        <td>1h 52m 30s (5:21/km)</td>
        <td>Base building 21k aerobic long run.</td>
      </tr>
    </tbody>
  </table>
  <p><em>Total 20K/21K+ Runs Logged: 6 sessions (including 2x 30ks and 1x 25k).</em></p>
</div>

<div class="card">
  <h2>📅 Week 15 Daily Workout Schedule (Garmin Synced)</h2>
  <table>
    <thead>
      <tr>
        <th>Day</th>
        <th>Activity</th>
        <th>Target / Details</th>
        <th>Location / Logistics</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Mon Sep 28</strong></td>
        <td>Recovery Shakeout / Rest</td>
        <td>4.0 km easy jog (&lt;145 bpm) or full rest. Flush quad soreness.</td>
        <td>Taft / Flat road</td>
      </tr>
      <tr>
        <td><strong>Tue Sep 29</strong></td>
        <td>Zone 2 Aerobic Cruise [6K]<br>+ Upper Push Strength</td>
        <td>4.5k Z2 (162-172 bpm) + 4x Chest press, cable triceps, core.<br><em>STRICT VETO ON LEGS.</em></td>
        <td>AF Taft / Treadmill (0%)</td>
      </tr>
      <tr>
        <td><strong>Wed Sep 30</strong></td>
        <td>Zone 2 Cruise + Strides [7.5K]</td>
        <td>6.0k Z2 (162-172 bpm) + 4x100m strides (3:45-3:55/km).<br><em>No heavy speed repeats.</em></td>
        <td>Taft / Track or Flat Road</td>
      </tr>
      <tr>
        <td><strong>Thu Oct 1</strong></td>
        <td>Indoor Bike Flush [35m]<br>+ Upper Pull Strength</td>
        <td><strong>Marikina Logistics:</strong> 35m indoor stationary bike (85-90 rpm, &lt;125 bpm, 0.0 GRF).<br>Upper Pull: Lat pulldowns, rows, rear delts, core.</td>
        <td>Marikina (No Swimming!)</td>
      </tr>
      <tr>
        <td><strong>Fri Oct 2</strong></td>
        <td>Pre-Long Run Shakeout [4K]</td>
        <td>4.0 km flat easy shakeout (&lt;148 bpm) in Puma Velocity Nitro 3s.<br>Carb loading day!</td>
        <td>Marikina / Flat road</td>
      </tr>
      <tr>
        <td><strong>Sat Oct 3</strong></td>
        <td>Cutback Aerobic Long Run [16K]</td>
        <td><strong>16.0 km Steady Zone 2 Cruise (162-172 bpm).</strong><br>Flat Marikina loop. Gels at Km 6 & 12.</td>
        <td>Marikina River Park / Roads</td>
      </tr>
      <tr>
        <td><strong>Sun Oct 4</strong></td>
        <td>Full Rest & Neuromuscular Reset</td>
        <td>0.0 km run. Complete rest, passive stretching, foam rolling quads/ITB.</td>
        <td>Home</td>
      </tr>
    </tbody>
  </table>
</div>

<div class="card">
  <h2>🩺 Physiological Symptom Remediation Protocol</h2>
  <h3>1. Painless Quad Twitching (Benign Muscle Fasciculations)</h3>
  <ul>
    <li><strong>Mechanism:</strong> Severe intracellular electrolyte displacement ($Mg^{2+}$, $Na^+$, $K^+$) & temporary $Ca^{2+}$ SERCA pump reuptake delay following 1h 48m heat sweat loss and glycogen depletion.</li>
    <li><strong>Protocol:</strong> Supplement 400mg Magnesium Glycinate daily at night, consume 1 packet hydration electrolytes in 750ml water daily, and ensure high carbohydrate restoration.</li>
  </ul>
  <h3>2. Painless Knee Cracking (Crepitus for ~2 weeks)</h3>
  <ul>
    <li><strong>Mechanism:</strong> Tightness in Vastus Lateralis and IT Band pulling patella slightly laterally during tracking.</li>
    <li><strong>Protocol:</strong> Foam roll outer quads and lateral quad sweep for 5 mins daily. Perform bodyweight VMO terminal knee extensions (TKEs) with band.</li>
  </ul>
</div>

<div class="card">
  <h2>⚙️ Framework Sanity Check Notice</h2>
  <p>Per your directive, tomorrow (Tuesday, Sep 29) we will execute a <strong>Long-Term Agent Framework Audit & Memory Sanity Check</strong> to refine memory persistence, state synchronization, and ensure zero context loss moving forward.</p>
</div>

</body>
</html>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = email_user
msg["To"] = recipient

msg.attach(MIMEText(html_content, "html"))

print(f"Sending Week 15 plan email to {recipient}...")
try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(email_user, email_pass)
    server.sendmail(email_user, recipient, msg.as_string())
    server.quit()
    print("[OK] Email sent successfully!")
except Exception as e:
    print(f"[ERR] Failed to send email: {e}")
