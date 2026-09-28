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

subject = "⚡ Marathon Agent: AUDITED & CORRECTED Week 15 Blueprint & Historical Run Audit"

html_content = """
<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
  .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
  h1 { color: #58a6ff; font-size: 24px; margin-top: 0; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
  h2 { color: #79c0ff; font-size: 18px; margin-top: 15px; }
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

<div class="card">
  <h1>🏃‍♂️ Marathon Agent — Audited & Corrected Week 15 Blueprint</h1>
  <p><span class="badge">VO2 MAX 59 ML/KG/MIN</span> <span class="badge-blue">GARMIN API VERIFIED</span> <span class="badge-warn">MON SEP 28 = FULL REST</span></p>
  <p>Hey Max, here is your fully audited and corrected <strong>Week 15 Schedule (Sep 28 – Oct 4, 2026)</strong> based directly on verified Garmin Connect API telemetry.</p>
</div>

<div class="card">
  <h2>🔍 Audit Verification & Corrections</h2>
  <ul>
    <li><strong>Flush Run Status (Sunday Sep 27 vs Monday Sep 28):</strong> Verified via Garmin API that you <strong>ALREADY completed a 3.0 km treadmill flush</strong> on Sunday, Sep 27 ('W14D7: Post-Long Run Recovery Fl', ID: 24511341372). Therefore, <strong>Today (Monday, Sep 28) is officially locked as FULL REST (0.0 km)</strong>. The 4k Monday workout has been removed from Garmin Connect.</li>
    <li><strong>30K Historical Run Verification:</strong> Verified directly from Garmin API historical data:
      <ul>
        <li><strong>2026-01-31:</strong> <span class="highlight">30.39 km</span> in 185.6 mins ('Awful but first 30k', ID: 23204918239)</li>
        <li><strong>2026-03-15:</strong> <span class="highlight">30.33 km</span> in 182.2 mins ('My second 30k', ID: 23419582103)</li>
      </ul>
      In August 2026, your long runs were <strong>20.64 km</strong> (Aug 15), <strong>24.02 km</strong> (Aug 23), and <strong>22.00 km</strong> (Aug 29). The previous summary table erroneously listed 30ks in August — this mapping error has been purged and corrected in the system database.</li>
  </ul>
</div>

<div class="card">
  <h2>📊 Ground Truth Historical Long Runs (>= 20K Logged in Garmin)</h2>
  <table>
    <thead>
      <tr>
        <th>Date</th>
        <th>Distance</th>
        <th>Duration / Pace</th>
        <th>Garmin Title / Notes</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>2026-09-26</td>
        <td><span class="highlight">21.39 km</span></td>
        <td>1h 48m (5:08/km)</td>
        <td>Concepcion Uno - Milestone Long Run (Matched HM PB in Heat, VO2Max 59)</td>
      </tr>
      <tr>
        <td>2026-09-19</td>
        <td><span class="highlight">20.07 km</span></td>
        <td>1h 47m (5:22/km)</td>
        <td>Rolling Hill 20k simulation 179m climbed (Treadmill)</td>
      </tr>
      <tr>
        <td>2026-09-06</td>
        <td><span class="highlight">20.01 km</span></td>
        <td>1h 53m (5:40/km)</td>
        <td>Treadmill Running (Double session day: +5.01k = 25.02k total)</td>
      </tr>
      <tr>
        <td>2026-08-29</td>
        <td><span class="highlight">22.00 km</span></td>
        <td>2h 02m (5:34/km)</td>
        <td>Treadmill Running</td>
      </tr>
      <tr>
        <td>2026-08-23</td>
        <td><span class="highlight">24.02 km</span></td>
        <td>2h 26m (6:07/km)</td>
        <td>Watching Ti while running on new treadmill</td>
      </tr>
      <tr>
        <td>2026-08-15</td>
        <td><span class="highlight">20.64 km</span></td>
        <td>1h 52m (5:25/km)</td>
        <td>Strongest Thunderstorm Run of 2026 so far</td>
      </tr>
      <tr>
        <td>2026-07-26</td>
        <td><span class="highlight">21.32 km</span></td>
        <td>1h 48m (5:07/km)</td>
        <td>Santa Elena 18-20km Step-Down</td>
      </tr>
      <tr>
        <td>2026-07-19</td>
        <td><span class="highlight">22.21 km</span></td>
        <td>1h 59m (5:23/km)</td>
        <td>UP Campus Long Run</td>
      </tr>
      <tr>
        <td><strong>2026-03-15</strong></td>
        <td><span class="highlight">30.33 km</span></td>
        <td>3h 02m (6:00/km)</td>
        <td><strong>My second 30k</strong></td>
      </tr>
      <tr>
        <td><strong>2026-01-31</strong></td>
        <td><span class="highlight">30.39 km</span></td>
        <td>3h 05m (6:06/km)</td>
        <td><strong>Awful but first 30k (Career All-Time Max)</strong></td>
      </tr>
    </tbody>
  </table>
</div>

<div class="card">
  <h2>📅 Corrected Week 15 Schedule</h2>
  <table>
    <thead>
      <tr>
        <th>Day</th>
        <th>Activity</th>
        <th>Target / Details</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Mon Sep 28</strong></td>
        <td><span class="highlight">FULL REST DAY (0.0 km)</span></td>
        <td>Flush completed Sunday (3.0k treadmill). Rest, hydrate, quad foam rolling.</td>
      </tr>
      <tr>
        <td><strong>Tue Sep 29</strong></td>
        <td>Zone 2 Aerobic Cruise [6K] + Upper Push</td>
        <td>6.0k Z2 (162-172 bpm) + Chest press, cable triceps, core. NO LEGS.</td>
      </tr>
      <tr>
        <td><strong>Wed Sep 30</strong></td>
        <td>Zone 2 Cruise + Strides [7.5K]</td>
        <td>6.0k Z2 + 4x100m strides (3:45-3:55/km).</td>
      </tr>
      <tr>
        <td><strong>Thu Oct 1</strong></td>
        <td>Indoor Bike Flush [35m] + Upper Pull</td>
        <td>Marikina 35m indoor bike (&lt;125 bpm, 85-90 rpm) + Lats/Rows/Rear Delts. NO SWIMMING.</td>
      </tr>
      <tr>
        <td><strong>Fri Oct 2</strong></td>
        <td>Pre-Long Run Shakeout [4K]</td>
        <td>4.0k flat easy shakeout (&lt;148 bpm) in Puma Velocity Nitro 3s. Carb loading!</td>
      </tr>
      <tr>
        <td><strong>Sat Oct 3</strong></td>
        <td>Cutback Aerobic Long Run [16K]</td>
        <td>16.0 km Steady Zone 2 Cruise (162-172 bpm). Flat Marikina route. Gels at Km 6 & 12.</td>
      </tr>
      <tr>
        <td><strong>Sun Oct 4</strong></td>
        <td>Full Rest & Reset</td>
        <td>0.0 km run. Complete rest.</td>
      </tr>
    </tbody>
  </table>
</div>

</body>
</html>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = subject
msg["From"] = email_user
msg["To"] = recipient
msg.attach(MIMEText(html_content, "html"))

print(f"Sending corrected email to {recipient}...")
try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(email_user, email_pass)
    server.sendmail(email_user, recipient, msg.as_string())
    server.quit()
    print("[OK] Corrected email sent successfully!")
except Exception as e:
    print(f"[ERR] Failed to send email: {e}")
