import os, sys, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv(r'c:/Users/Max/OneDrive - De La Salle University - Manila/marathon-agent/.env')

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT   = 587
FROM_EMAIL  = os.getenv('GARMIN_EMAIL')
APP_PASS    = os.getenv('GMAIL_APP_PASSWORD')
TO_EMAIL    = 'maxxsotelo@gmail.com'

subject = 'Antigravity Monthly Performance Audit: August 2026 Comprehensive Review'

html_content = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Antigravity Monthly Performance Audit</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0e14; color: #e2e8f0; line-height: 1.6; padding: 20px 0; }
  .wrapper { max-width: 740px; margin: 0 auto; background: #0f131c; border: 1px solid #1e2638; border-radius: 12px; overflow: hidden; }
  .header { background: linear-gradient(135deg, #131c2e 0%, #0a0e17 100%); padding: 36px 36px 28px; border-bottom: 2px solid #38ef7d; }
  .logo { font-size: 11px; letter-spacing: 3.5px; color: #38ef7d; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }
  .header h1 { font-size: 26px; font-weight: 800; color: #ffffff; margin-bottom: 6px; }
  .header .subtitle { font-size: 13px; color: #94a3b8; }
  .section { padding: 28px 36px; border-bottom: 1px solid #1e2638; }
  .section-title { font-size: 12px; letter-spacing: 2.5px; color: #38ef7d; text-transform: uppercase; margin-bottom: 18px; font-weight: 700; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
  .grid-4 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px; }
  .card { background: #141a29; border: 1px solid #232d42; border-radius: 8px; padding: 14px 16px; }
  .card .label { font-size: 10px; color: #8fa0ba; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
  .card .val { font-size: 22px; font-weight: 800; color: #ffffff; }
  .card .sub { font-size: 11px; color: #38ef7d; margin-top: 3px; font-weight: 500; }
  .card.highlight { border-color: #38ef7d; background: #0e2a1e; }
  .card.highlight .val { color: #38ef7d; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; margin-bottom: 14px; }
  th { background: #161e30; color: #94a3b8; text-align: left; padding: 10px 12px; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; border-bottom: 1px solid #25314a; }
  td { padding: 10px 12px; border-bottom: 1px solid #1a2236; color: #cbd5e1; }
  tr:nth-child(even) { background: #111724; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
  .badge-cyan { background: rgba(0,242,254,0.15); color: #00f2fe; border: 1px solid rgba(0,242,254,0.3); }
  .badge-green { background: rgba(56,239,125,0.15); color: #38ef7d; border: 1px solid rgba(56,239,125,0.3); }
  .badge-gold { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
  .block { background: #141a29; border-left: 3px solid #38ef7d; border-radius: 4px; padding: 14px 18px; margin-bottom: 12px; }
  .block.gold { border-left-color: #f59e0b; }
  .block.blue { border-left-color: #00f2fe; }
  .block-title { font-size: 13px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
  .block-desc { font-size: 12px; color: #94a3b8; line-height: 1.6; }
  .footer { padding: 24px 36px; text-align: center; background: #090c12; font-size: 11px; color: #475569; }
</style>
</head>
<body>
<div class="wrapper">

  <!-- HEADER -->
  <div class="header">
    <div class="logo">Antigravity Performance Lab &bull; Monthly Division</div>
    <h1>August 2026 Monthly Performance Audit</h1>
    <div class="subtitle">Athlete: <strong>Max Sotelo</strong> &nbsp;|&nbsp; Period: <strong>August 1 &ndash; August 31, 2026</strong> &nbsp;|&nbsp; Verified Telemetry</div>
  </div>

  <!-- SECTION 1: MONTHLY VOLUME & TOTALS -->
  <div class="section">
    <div class="section-title">1. August 2026 Executive Summary &amp; Totals</div>
    <div class="grid-4">
      <div class="card highlight">
        <div class="label">Total Running Volume</div>
        <div class="val">194.96 km</div>
        <div class="sub">Across 23 Running Sessions</div>
      </div>
      <div class="card">
        <div class="label">Total Time on Feet</div>
        <div class="val">18.29 Hours</div>
        <div class="sub">18h 17m Total Running Duration</div>
      </div>
      <div class="card">
        <div class="label">Cross-Training Volume</div>
        <div class="val">6,425 Meters</div>
        <div class="sub">5 Pool Swims + 7 Strength Sessions</div>
      </div>
      <div class="card highlight">
        <div class="label">Workout Calories Torched</div>
        <div class="val">18,687 kcal</div>
        <div class="sub">54 Total Activities Logged</div>
      </div>
    </div>
  </div>

  <!-- SECTION 2: THE 4 MAJOR LONG RUNS -->
  <div class="section">
    <div class="section-title">2. August Crown-Jewel Long Runs (&ge; 18.0 km)</div>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Session Name / Surface</th>
          <th>Distance</th>
          <th>Avg HR</th>
          <th>Training Effect</th>
          <th>Calories</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Aug 09</strong></td>
          <td>Treadmill Aerobic Progression</td>
          <td><strong>19.20 km</strong></td>
          <td>149 bpm</td>
          <td><span class="badge badge-green">3.2 Aerobic</span></td>
          <td>981 kcal</td>
        </tr>
        <tr>
          <td><strong>Aug 15</strong></td>
          <td>Monsoon Thunderstorm Run (Road)</td>
          <td><strong>20.64 km</strong></td>
          <td>149 bpm</td>
          <td><span class="badge badge-cyan">3.9 Aerobic (VO2Max 58!)</span></td>
          <td>1,341 kcal</td>
        </tr>
        <tr>
          <td><strong>Aug 23</strong></td>
          <td>NordicTrack Milestone Long Run</td>
          <td><strong>24.02 km</strong></td>
          <td>148 bpm</td>
          <td><span class="badge badge-green">3.6 Aerobic</span></td>
          <td>1,404 kcal</td>
        </tr>
        <tr>
          <td><strong>Aug 29</strong></td>
          <td>Step-Down Consolidation (Treadmill)</td>
          <td><strong>22.00 km</strong></td>
          <td>150 bpm</td>
          <td><span class="badge badge-green">3.7 Aerobic (4:07 kick!)</span></td>
          <td>1,262 kcal</td>
        </tr>
      </tbody>
    </table>
    <div class="block gold">
      <div class="block-title">August Milestone Achievement:</div>
      <div class="block-desc">
        August cemented your <strong>20th career 21km+ half-marathon milestone</strong>. Your aerobic cardiac drift over 20+ km has virtually disappeared, averaging a cool <strong>148&ndash;150 bpm</strong> even at the 2-hour mark!
      </div>
    </div>
  </div>

  <!-- SECTION 3: PHYSIOLOGICAL METAMORPHOSIS -->
  <div class="section">
    <div class="section-title">3. Physiological Metamorphosis in August</div>
    <div class="grid-2">
      <div class="card highlight">
        <div class="label">Body Weight Shift</div>
        <div class="val">-2.15 kg</div>
        <div class="sub">70.80 kg ➔ 68.65 kg (New Cycle Low!)</div>
      </div>
      <div class="card">
        <div class="label">VO2 Max Progression</div>
        <div class="val">58.0 mL/kg</div>
        <div class="sub">Jumped from 57.0 on Aug 15 (Top 1%)</div>
      </div>
    </div>
    <p style="font-size:12px; color:#94a3b8;">
      &bull; <strong>Resting Heart Rate:</strong> Settled into the elite <strong>36&ndash;38 bpm</strong> envelope.<br>
      &bull; <strong>Speed Reserve Breakthrough:</strong> Broken 5k PR twice during typhoon weather (Aug 5 &amp; Aug 6), proving that higher volume was translating directly into explosive speed!
    </p>
  </div>

  <!-- SECTION 4: TREADMILL LONG RUN STRATEGY & ROAD TO 35K -->
  <div class="section">
    <div class="section-title">4. Strategic Directives for September &amp; The Road to 35K</div>
    <div class="block blue">
      <div class="block-title">Treadmill Long Run Protocol (Approved &amp; Preferred):</div>
      <div class="block-desc">
        You have officially designated the <strong>NordicTrack S20i Treadmill (@ 1.0% Incline + Direct Fan)</strong> as your favored arena for Long Runs (20k&ndash;35k).<br>
        <strong>Why this is a Masterstroke:</strong><br>
        1. <strong>Frictionless Fueling:</strong> Gels, bananas, water, and electrolyte bottles sit right on the console cup holders with zero bottle-holding arm fatigue.<br>
        2. <strong>Zero Environmental Hazards:</strong> 100% immune to tropical downpours, street traffic, potholes, or stray animals.<br>
        3. <strong>Pacing Precision:</strong> Belt locks in your exact Zone 2 tempo with zero drift.
      </div>
    </div>
    <div class="block gold">
      <div class="block-title">September Escalation Path (Surpassing Your 30.39k All-Time Base):</div>
      <div class="block-desc">
        &bull; <strong>Week 11 (Sun, Sep 06):</strong> 24.0 &ndash; 25.0 km (Consolidate 25k)<br>
        &bull; <strong>Week 12 (Sun, Sep 13):</strong> 27.0 &ndash; 28.0 km (Pushing the envelope)<br>
        &bull; <strong>Week 13 (Sun, Sep 20):</strong> 21.0 &ndash; 22.0 km (Consolidation Step-Down)<br>
        &bull; <strong>Week 14 (Sun, Sep 27):</strong> 30.0 &ndash; 31.0 km (Re-claiming the 30k benchmark at 68.6kg!)<br>
        &bull; <strong>Week 15 (Sun, Oct 04):</strong> <strong>32.0 &ndash; 35.0 km (THE ALL-TIME RECORD: 20&ndash;22 MILES! 👑)</strong>
      </div>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <p>Antigravity AI Coaching System &bull; Single Source of Truth &bull; Garmin Firstbeat Telemetry Verified</p>
    <p style="color:#64748b; margin-top:4px;">Delivered to Max Sotelo (maxxsotelo@gmail.com) on September 3, 2026</p>
  </div>

</div>
</body>
</html>'''

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From']    = FROM_EMAIL
msg['To']      = TO_EMAIL
msg.attach(MIMEText(html_content, 'html'))

server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(FROM_EMAIL, APP_PASS)
server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
server.quit()
print('SUCCESSFULLY SENT MONTHLY AUDIT EMAIL TO:', TO_EMAIL)
