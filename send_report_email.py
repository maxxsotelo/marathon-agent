"""
send_report_email.py — Antigravity Weekly Report Email Sender
Sends the exhaustive run analysis + weekly training recommendations to maxxsotelo@gmail.com
"""

import os, sys, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")

# ---- CONFIG ----
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
FROM_EMAIL  = os.getenv("GARMIN_EMAIL")
APP_PASS    = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL    = "maxxsotelo@gmail.com"

# ---- LOAD REPORT ----
report_path = r"C:\Users\Max\.gemini\antigravity\brain\491e4690-66cd-499d-9776-017b0087dbe4\artifacts\run_analysis_20260523.md"
with open(report_path, "r", encoding="utf-8") as f:
    report_md = f.read()

# ---- BUILD HTML EMAIL ----
html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Antigravity Weekly Report</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #0d0f14; color: #e8eaf0; }
  .wrapper { max-width: 720px; margin: 0 auto; background: #0d0f14; }
  .header { background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%); padding: 40px 40px 30px; border-bottom: 2px solid #00d4aa; }
  .logo { font-size: 11px; letter-spacing: 4px; color: #00d4aa; text-transform: uppercase; margin-bottom: 12px; }
  .header h1 { font-size: 28px; font-weight: 700; color: #ffffff; line-height: 1.2; }
  .header .subtitle { font-size: 14px; color: #8892a4; margin-top: 8px; }
  .section { padding: 32px 40px; border-bottom: 1px solid #1e2535; }
  .section-title { font-size: 13px; letter-spacing: 3px; color: #00d4aa; text-transform: uppercase; margin-bottom: 20px; font-weight: 600; }
  .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
  .metric-card { background: #141824; border: 1px solid #1e2535; border-radius: 8px; padding: 16px; }
  .metric-card .label { font-size: 11px; color: #8892a4; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
  .metric-card .value { font-size: 22px; font-weight: 700; color: #ffffff; }
  .metric-card .unit { font-size: 12px; color: #8892a4; margin-left: 4px; }
  .metric-card .note { font-size: 11px; color: #00d4aa; margin-top: 4px; }
  .metric-card.alert { border-color: #ff6b6b; }
  .metric-card.alert .value { color: #ff6b6b; }
  .metric-card.good { border-color: #00d4aa; }
  .metric-card.good .value { color: #00d4aa; }
  .metric-card.warn { border-color: #ffd166; }
  .metric-card.warn .value { color: #ffd166; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
  th { background: #141824; color: #8892a4; text-align: left; padding: 8px 10px; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #1e2535; }
  td { padding: 8px 10px; border-bottom: 1px solid #1a2030; color: #cdd5e0; }
  tr:hover td { background: #141824; }
  .z1 { color: #8892a4; } .z2 { color: #00d4aa; } .z3 { color: #ffd166; } .z4 { color: #ff9f43; } .z5 { color: #ff6b6b; }
  .phase-block { background: #141824; border-left: 3px solid #00d4aa; border-radius: 4px; padding: 16px 20px; margin-bottom: 12px; }
  .phase-block.warn { border-color: #ffd166; }
  .phase-block.hot { border-color: #ff6b6b; }
  .phase-title { font-size: 13px; font-weight: 700; color: #ffffff; margin-bottom: 6px; }
  .phase-body { font-size: 13px; color: #8892a4; line-height: 1.6; }
  .week-day { background: #141824; border: 1px solid #1e2535; border-radius: 8px; padding: 16px 20px; margin-bottom: 10px; }
  .week-day .day-label { font-size: 11px; letter-spacing: 2px; color: #00d4aa; text-transform: uppercase; margin-bottom: 6px; }
  .week-day .day-workout { font-size: 15px; font-weight: 600; color: #ffffff; margin-bottom: 4px; }
  .week-day .day-note { font-size: 12px; color: #8892a4; line-height: 1.5; }
  .verdict { background: linear-gradient(135deg, #0a1628 0%, #0d1117 100%); border: 1px solid #00d4aa; border-radius: 10px; padding: 24px; margin-top: 8px; }
  .verdict p { font-size: 13px; color: #cdd5e0; line-height: 1.7; margin-bottom: 10px; }
  .verdict p:last-child { margin-bottom: 0; }
  .footer { padding: 28px 40px; text-align: center; background: #080b10; }
  .footer p { font-size: 11px; color: #3d4a5c; line-height: 1.7; }
  .footer .brand { color: #00d4aa; font-weight: 700; letter-spacing: 2px; }
  .divider { height: 1px; background: linear-gradient(to right, transparent, #00d4aa, transparent); margin: 8px 0; }
  .flag-warn { color: #ffd166; font-size: 11px; }
  .flag-ok { color: #00d4aa; font-size: 11px; }
  .flag-alert { color: #ff6b6b; font-size: 11px; }
</style>
</head>
<body>
<div class="wrapper">

  <!-- HEADER -->
  <div class="header">
    <div class="logo">Antigravity Agent &mdash; Performance Lab</div>
    <h1>Weekly Run Report &amp; Training Brief</h1>
    <div class="subtitle">Athlete: Max Sotelo &nbsp;&bull;&nbsp; Report Date: May 24, 2026 &nbsp;&bull;&nbsp; Activity: May 23, 2026 Long Run</div>
  </div>

  <!-- KIAT ENGINE SUMMARY -->
  <div class="section">
    <div class="section-title">Kiat Engine &mdash; Sunday Vitals</div>
    <div class="metric-grid">
      <div class="metric-card good">
        <div class="label">Training Readiness Score</div>
        <div class="value">86.1<span class="unit">/ 100</span></div>
        <div class="note">Primed &mdash; cleared for training</div>
      </div>
      <div class="metric-card warn">
        <div class="label">ACWR (Acute:Chronic Load)</div>
        <div class="value">1.43</div>
        <div class="note">High Zone &mdash; reduce volume 3-5 days</div>
      </div>
      <div class="metric-card good">
        <div class="label">HRV Status</div>
        <div class="value">100<span class="unit">%</span></div>
        <div class="note">Autonomic nervous system balanced</div>
      </div>
      <div class="metric-card good">
        <div class="label">Training Status</div>
        <div class="value" style="font-size:16px">Productive</div>
        <div class="note">Positive adaptation occurring</div>
      </div>
    </div>
  </div>

  <!-- RUN OVERVIEW -->
  <div class="section">
    <div class="section-title">Activity Overview &mdash; UP Campus Long Run (May 23)</div>
    <div class="metric-grid">
      <div class="metric-card">
        <div class="label">Total Distance</div>
        <div class="value">21.27<span class="unit">km</span></div>
      </div>
      <div class="metric-card">
        <div class="label">Moving Time</div>
        <div class="value">2h 16m<span class="unit">58s</span></div>
      </div>
      <div class="metric-card">
        <div class="label">Average Pace</div>
        <div class="value">6:27<span class="unit">/km</span></div>
        <div class="note">GAP: 6:31/km</div>
      </div>
      <div class="metric-card warn">
        <div class="label">Calories Burned</div>
        <div class="value">1,774<span class="unit">kcal</span></div>
        <div class="note">1,572 active + 202 BMR</div>
      </div>
      <div class="metric-card warn">
        <div class="label">Sweat Loss</div>
        <div class="value">2,288<span class="unit">mL</span></div>
        <div class="note">Must replace with electrolytes</div>
      </div>
      <div class="metric-card">
        <div class="label">Body Battery Cost</div>
        <div class="value">-15<span class="unit">pts</span></div>
      </div>
    </div>
  </div>

  <!-- ADVANCED HR METRICS -->
  <div class="section">
    <div class="section-title">Advanced Heart Rate Analysis</div>
    <div class="metric-grid">
      <div class="metric-card warn">
        <div class="label">TRIMP (Banister)</div>
        <div class="value">231.5<span class="unit">AU</span></div>
        <div class="note">High load &mdash; major recovery demand</div>
      </div>
      <div class="metric-card warn">
        <div class="label">PA:HR Decoupling</div>
        <div class="value">6.3<span class="unit">%</span></div>
        <div class="note">Moderate &mdash; 5% threshold exceeded</div>
      </div>
      <div class="metric-card alert">
        <div class="label">Cardiac Drift</div>
        <div class="value">+17.7<span class="unit">bpm</span></div>
        <div class="note">Severe &mdash; plasma loss from 30-34&deg;C heat</div>
      </div>
      <div class="metric-card good">
        <div class="label">EPOC (Session)</div>
        <div class="value">112<span class="unit">mL/kg</span></div>
        <div class="note">Significant recovery oxygen debt</div>
      </div>
      <div class="metric-card">
        <div class="label">Max HR Drop</div>
        <div class="value">-17<span class="unit">bpm</span></div>
        <div class="note">Lap 9 &mdash; walk/recovery event</div>
      </div>
      <div class="metric-card good">
        <div class="label">Edwards TRIMP</div>
        <div class="value">~195<span class="unit">AU</span></div>
        <div class="note">Zone-weighted training load</div>
      </div>
    </div>

    <div class="section-title" style="margin-top:24px">Time in Real HR Zones (Max&rsquo;s Verified Zones)</div>
    <table>
      <tr>
        <th>Zone</th><th>Boundary</th><th>Time</th><th>% of Run</th><th>Energy System</th>
      </tr>
      <tr><td class="z1"><b>Z1: Recovery</b></td><td>&lt;145 bpm</td><td>~68m</td><td>~49%</td><td>Fat oxidation only</td></tr>
      <tr><td class="z2"><b>Z2: Aerobic</b></td><td>145-162 bpm</td><td>~54m</td><td>~39%</td><td>Fat + carb. Mitochondria stimulus.</td></tr>
      <tr><td class="z3"><b>Z3: Grey/MP</b></td><td>163-184 bpm</td><td>~16m</td><td>~11%</td><td>Glycolytic. Fast finish laps.</td></tr>
      <tr><td class="z4"><b>Z4: Threshold</b></td><td>185-196 bpm</td><td>0m</td><td>0%</td><td>&mdash;</td></tr>
      <tr><td class="z5"><b>Z5: Anaerobic</b></td><td>197+ bpm</td><td>0m</td><td>0%</td><td>&mdash;</td></tr>
    </table>
  </div>

  <!-- LAP SUMMARY -->
  <div class="section">
    <div class="section-title">Lap Summary</div>
    <table>
      <tr><th>Lap</th><th>Pace</th><th>Avg HR</th><th>Zone</th><th>Stride (cm)</th><th>GCT (ms)</th><th>Power (W)</th><th>TRIMP</th><th>Temp</th></tr>
      <tr><td>1</td><td>6:26</td><td class="z1">141</td><td class="z1">Z1</td><td>93.3</td><td>274</td><td>283</td><td>6.2</td><td>32-33&deg;C</td></tr>
      <tr><td>2</td><td>6:38</td><td class="z2">152</td><td class="z2">Z2</td><td>89.9</td><td>275</td><td>266</td><td>8.3</td><td>33&deg;C</td></tr>
      <tr><td>3</td><td>7:09</td><td class="z2">151</td><td class="z2">Z2</td><td>83.9</td><td>285</td><td>258</td><td>7.9</td><td>33-34&deg;C</td></tr>
      <tr><td>4</td><td>7:17</td><td class="z1">147</td><td class="z1">Z1</td><td>81.7</td><td>284</td><td>246</td><td>7.1</td><td>32-33&deg;C</td></tr>
      <tr><td>5</td><td>8:06</td><td class="z1">142</td><td class="z1">Z1</td><td>80.6</td><td><b style="color:#ffd166">336</b></td><td>227</td><td>5.6</td><td>32&deg;C</td></tr>
      <tr><td>6</td><td>7:17</td><td class="z1">145</td><td class="z1">Z1</td><td>80.8</td><td>279</td><td>232</td><td>6.6</td><td>32-33&deg;C</td></tr>
      <tr><td>7</td><td>7:09</td><td class="z2">154</td><td class="z2">Z2</td><td>82.4</td><td>280</td><td>253</td><td>8.7</td><td>32-33&deg;C</td></tr>
      <tr><td>8</td><td>6:33</td><td class="z2">157</td><td class="z2">Z2</td><td>91.1</td><td>272</td><td>292</td><td>10.3</td><td>33-34&deg;C</td></tr>
      <tr><td>9</td><td>7:26</td><td class="z1">140</td><td class="z1">Z1</td><td>80.9</td><td>287</td><td>229</td><td>5.8</td><td>33-34&deg;C</td></tr>
      <tr><td>10</td><td>6:08</td><td class="z2">155</td><td class="z2">Z2</td><td>92.5</td><td><b style="color:#00d4aa">262</b></td><td>280</td><td>9.8</td><td>33&deg;C</td></tr>
      <tr><td>11</td><td>6:18</td><td class="z2">154</td><td class="z2">Z2</td><td>94.6</td><td>267</td><td>295</td><td>9.2</td><td>33&deg;C</td></tr>
      <tr><td>12</td><td>6:11</td><td class="z2">156</td><td class="z2">Z2</td><td>91.4</td><td><b style="color:#00d4aa">262</b></td><td>280</td><td>9.9</td><td>33&deg;C</td></tr>
      <tr><td>13</td><td>6:16</td><td class="z2">160</td><td class="z2">Z2</td><td>91.1</td><td>264</td><td>291</td><td>11.1</td><td>33-34&deg;C</td></tr>
      <tr><td>14</td><td>6:44</td><td class="z2">151</td><td class="z2">Z2</td><td>87.7</td><td>272</td><td>295</td><td>8.0</td><td>33-34&deg;C</td></tr>
      <tr><td>15</td><td>6:14</td><td class="z1">148</td><td class="z1">Z1</td><td>92.6</td><td>268</td><td>282</td><td>8.5</td><td>33&deg;C</td></tr>
      <tr><td>16</td><td>6:24</td><td class="z2">157</td><td class="z2">Z2</td><td>89.3</td><td>266</td><td>284</td><td>10.6</td><td>33-34&deg;C</td></tr>
      <tr><td>17</td><td>6:22</td><td class="z2">162</td><td class="z2">Z2</td><td>90.2</td><td>267</td><td>284</td><td>12.0</td><td>33-34&deg;C</td></tr>
      <tr><td><b>18</b></td><td><b>5:42</b></td><td class="z3"><b>167</b></td><td class="z3"><b>Z3</b></td><td><b>99.4</b></td><td><b style="color:#00d4aa">255</b></td><td><b>304</b></td><td><b>14.3</b></td><td>33-34&deg;C</td></tr>
      <tr><td><b>19</b></td><td><b>5:46</b></td><td class="z3"><b>172</b></td><td class="z3"><b>Z3</b></td><td><b>98.1</b></td><td><b style="color:#00d4aa">255</b></td><td><b>311</b></td><td><b>16.5</b></td><td>33&deg;C</td></tr>
      <tr><td><b>20</b></td><td><b>5:45</b></td><td class="z3"><b>173</b></td><td class="z3"><b>Z3</b></td><td><b>98.4</b></td><td><b style="color:#00d4aa">257</b></td><td><b>318</b></td><td><b>16.9</b></td><td>33-34&deg;C</td></tr>
      <tr><td><b>21</b></td><td><b>5:20</b></td><td class="z3"><b>177</b></td><td class="z3"><b>Z3</b></td><td><b style="color:#00d4aa">103.3</b></td><td><b style="color:#00d4aa">248</b></td><td><b>316</b></td><td><b>18.7</b></td><td>34&deg;C</td></tr>
    </table>
  </div>

  <!-- BIOMECHANICS -->
  <div class="section">
    <div class="section-title">Biomechanics &mdash; Overall</div>
    <div class="metric-grid">
      <div class="metric-card">
        <div class="label">Avg Cadence</div>
        <div class="value">169<span class="unit">spm</span></div>
        <div class="note">Peaks to 179 spm on the kick</div>
      </div>
      <div class="metric-card">
        <div class="label">Avg Stride Length</div>
        <div class="value">89.5<span class="unit">cm</span></div>
        <div class="note">Peaks to 103.3 cm on Lap 21</div>
      </div>
      <div class="metric-card good">
        <div class="label">Avg GCT</div>
        <div class="value">274<span class="unit">ms</span></div>
        <div class="note">Drops to elite 248ms on the kick</div>
      </div>
      <div class="metric-card good">
        <div class="label">Vertical Oscillation</div>
        <div class="value">8.1<span class="unit">cm</span></div>
        <div class="note">Below 8.5cm target &mdash; efficient</div>
      </div>
      <div class="metric-card good">
        <div class="label">Vertical Ratio</div>
        <div class="value">9.1<span class="unit">%</span></div>
        <div class="note">Driven up by slow pacing block laps</div>
      </div>
      <div class="metric-card good">
        <div class="label">FBI Score</div>
        <div class="value">100<span class="unit">/100</span></div>
        <div class="note">Zero form collapse &mdash; elite durability</div>
      </div>
    </div>
  </div>

  <!-- PHASE ANALYSIS -->
  <div class="section">
    <div class="section-title">Run Phase Analysis</div>

    <div class="phase-block">
      <div class="phase-title">Phase 1 &mdash; The Brother Pace (Laps 1-9)</div>
      <div class="phase-body">You were forced to run between 6:26/km and 8:06/km. GCT spiked to 336ms on Lap 5 because you were mechanically braking to stay slow. Your HR sat perfectly between 140-157 bpm. <b>Result: Zero glycogen burned. 100% fat oxidation. Perfect heat protection.</b></div>
    </div>

    <div class="phase-block">
      <div class="phase-title">Phase 2 &mdash; The Solo Aerobic Engine (Laps 10-17)</div>
      <div class="phase-body">Your natural Zone 2 mechanics unlocked immediately on Lap 10. Cadence jumped to 174 spm, stride opened to 92cm, GCT dropped to 262ms. You held 280-295 Watts effortlessly. HR stayed within the 162 bpm cap until Lap 17 where you hit the ceiling exactly. <b>Textbook Zone 2 execution.</b></div>
    </div>

    <div class="phase-block warn">
      <div class="phase-title">Phase 3 &mdash; The Marathon Pace Kick (Laps 18-21)</div>
      <div class="phase-body">You switched to glycolytic mode. Stride length exploded to 98-103cm. GCT dropped to an elite 248ms. Power peaked at 318W. HR climbed to 177 bpm. Your biomechanics did not collapse &mdash; they improved. <b>FBI: 100/100. Zero form degradation. The strength training protocol is working.</b></div>
    </div>
  </div>

  <!-- WEEKLY PLAN -->
  <div class="section">
    <div class="section-title">Recommended Week Ahead &mdash; Placeholder (Daily Vitals Override)</div>
    <p style="font-size:12px;color:#8892a4;margin-bottom:16px;">Note: All sessions below are placeholder prescriptions. Actual workout selection and intensity will be confirmed each morning based on live Kiat Engine diagnostics (TRS, ACWR, HRV). If ACWR stays elevated (&gt;1.30) into mid-week, intensity sessions will be vetoed automatically.</p>

    <div class="week-day">
      <div class="day-label">Sunday, May 25 &mdash; Today</div>
      <div class="day-workout">Complete Rest / Girlfriend&rsquo;s Birthday</div>
      <div class="day-note">No training. ACWR is at 1.43 &mdash; active rest is the highest-value action today. Prioritize protein and glycogen replenishment. Enjoy the celebration.</div>
    </div>

    <div class="week-day">
      <div class="day-label">Monday, May 26</div>
      <div class="day-workout">Active Recovery &mdash; 45-min Zone 1 Bike or Rest</div>
      <div class="day-note">HR cap: 135 bpm. No running. Goal is to flush metabolic waste and lower ACWR. If legs feel heavy, take full rest instead. Confirm via morning vitals.</div>
    </div>

    <div class="week-day">
      <div class="day-label">Tuesday, May 27</div>
      <div class="day-workout">Easy Run + Strides OR Kenyan Core Circuit</div>
      <div class="day-note">50-60 min easy run capped at 162 bpm + 6 strides, OR Kenyan Core if running volume is still too high per ACWR. Not both. Morning vitals will determine. DO NOT run if ACWR &gt; 1.30.</div>
    </div>

    <div class="week-day">
      <div class="day-label">Wednesday, May 28</div>
      <div class="day-workout">Quality Session &mdash; VO2 Max or Threshold Intervals</div>
      <div class="day-note">Placeholder: 8x600m Zone 5 OR 4x2km Zone 4. Only executed if TRS &gt; 75 AND ACWR &lt; 1.30 AND HRV is balanced. This is the week&rsquo;s single hard running session.</div>
    </div>

    <div class="week-day">
      <div class="day-label">Thursday, May 29</div>
      <div class="day-workout">Kenyan Core Circuit + Optional Easy Jog</div>
      <div class="day-note">Core work to reinforce the structural gains from this week. Optional 20-30 min easy flush run if legs feel good. Separation from Wednesday quality session: minimum 6 hours.</div>
    </div>

    <div class="week-day">
      <div class="day-label">Friday, May 30</div>
      <div class="day-workout">Structural Rest or Light Bike</div>
      <div class="day-note">Protect the Chassis for Saturday&rsquo;s long run. Zero high-impact work. Electrolyte loading and carbohydrate top-up in the evening.</div>
    </div>

    <div class="week-day">
      <div class="day-label">Saturday, May 31</div>
      <div class="day-workout">Maintenance Long Run &mdash; 18-22 km Zone 2</div>
      <div class="day-note">Cap: 162 bpm strictly. The 17.7 bpm cardiac drift from this week is a warning &mdash; ensure full hydration before heading out. Wear moisture-wicking gear only. Take a gel at km 10.</div>
    </div>
  </div>

  <!-- VERDICT -->
  <div class="section">
    <div class="section-title">Coaching Verdict</div>
    <div class="verdict">
      <p><b style="color:#00d4aa">Strength Training Is Working.</b> Your FBI score of 100/100 at kilometer 21 is the clearest proof yet. Most runners shuffle and collapse in the last 3km of a 21km run. You accelerated, opened your stride to 103cm, and dropped your ground contact time to 248ms. Your tendons are acting like compressed springs.</p>
      <p><b style="color:#ffd166">The Heat Tax Is Real.</b> A 17.7 bpm cardiac drift over 2 hours in 30-34&deg;C heat is severe. This is NOT fitness failure &mdash; this is physics. Your plasma volume drops, your blood thickens, and your heart beats faster to compensate. The fix is aggressive pre-run hydration and moisture-wicking gear only.</p>
      <p><b style="color:#ff6b6b">ACWR Alert (1.43).</b> You are approaching the danger zone ceiling (1.50). Do not add any unplanned running this week. Let the chronic base catch up. By Wednesday, your ACWR should settle back into the Sweet Spot naturally.</p>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <p class="brand">ANTIGRAVITY</p>
    <p>Powered by the Kiat Engine &mdash; Custom Physiological Intelligence Layer<br>
    Garmin Forerunner 165 &bull; Real HR Zones &bull; Banister TRIMP &bull; Knuttgen EPOC Model<br>
    <br>This report is generated automatically. All training decisions should be confirmed with live morning vitals.</p>
  </div>

</div>
</body>
</html>
"""

# ---- BUILD PLAIN TEXT FALLBACK ----
plain = """ANTIGRAVITY — Weekly Run Report | May 24, 2026

KIAT ENGINE VITALS
TRS: 86.1/100 (Primed) | ACWR: 1.43 (High) | HRV: Balanced | Status: Productive

RUN SUMMARY — May 23, 2026 (UP Campus — 21.1km)
Distance: 21.27 km | Time: 2h 16m | Avg Pace: 6:27/km
Calories: 1,774 kcal | Sweat Loss: 2,288 mL | Body Battery: -15 pts

ADVANCED HR METRICS
TRIMP (Banister): 231.5 AU
PA:HR Decoupling: 6.3% (moderate)
Cardiac Drift: +17.7 bpm (severe — plasma loss in 34C heat)
EPOC (Session): 112 mL/kg
Max HR Drop: -17 bpm (Lap 9 — walk event)

BIOMECHANICS
Avg GCT: 274ms | Peak GCT (kick): 248ms (elite)
Avg Stride: 89.5cm | Peak Stride: 103.3cm
FBI: 100/100 — ZERO form collapse
Aerobic Training Effect: 3.9/5.0 (Improving Aerobic Endurance)

WEEKLY PLAN (Placeholder — confirmed daily via Kiat Engine)
Sun May 25: REST — Birthday celebration
Mon May 26: Active Recovery Bike (Zone 1, 45min) or Rest
Tue May 27: Easy Run 50-60min (162 bpm cap) + 6 strides OR Kenyan Core
Wed May 28: Quality — 8x600m VO2 Max OR 4x2km Threshold (if ACWR <1.30)
Thu May 29: Kenyan Core + Optional easy jog
Fri May 30: Structural rest
Sat May 31: Maintenance Long Run 18-22km Zone 2

Antigravity Agent | Powered by Kiat Engine
"""

# ---- SEND ----
msg = MIMEMultipart("alternative")
msg["Subject"] = "Antigravity | Weekly Run Report & Training Plan — May 24, 2026"
msg["From"]    = f"Antigravity Agent <{FROM_EMAIL}>"
msg["To"]      = TO_EMAIL

msg.attach(MIMEText(plain, "plain"))
msg.attach(MIMEText(html, "html"))

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(FROM_EMAIL, APP_PASS)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
    print("[OK] Email sent successfully to", TO_EMAIL)
except Exception as e:
    print("[ERROR]", e)
