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

subject = 'Antigravity Master Progress Audit: 2026 Buildup Transformation & Strategic Roadmap'

html_content = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Antigravity Master Progress Audit</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0e14; color: #e2e8f0; line-height: 1.6; padding: 20px 0; }
  .wrapper { max-width: 740px; margin: 0 auto; background: #0f131c; border: 1px solid #1e2638; border-radius: 12px; overflow: hidden; }
  .header { background: linear-gradient(135deg, #131c2e 0%, #0a0e17 100%); padding: 36px 36px 28px; border-bottom: 2px solid #00f2fe; }
  .logo { font-size: 11px; letter-spacing: 3.5px; color: #00f2fe; text-transform: uppercase; font-weight: 700; margin-bottom: 10px; }
  .header h1 { font-size: 26px; font-weight: 800; color: #ffffff; margin-bottom: 6px; }
  .header .subtitle { font-size: 13px; color: #94a3b8; }
  .section { padding: 28px 36px; border-bottom: 1px solid #1e2638; }
  .section-title { font-size: 12px; letter-spacing: 2.5px; color: #00f2fe; text-transform: uppercase; margin-bottom: 18px; font-weight: 700; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
  .grid-4 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px; }
  .card { background: #141a29; border: 1px solid #232d42; border-radius: 8px; padding: 14px 16px; }
  .card .label { font-size: 10px; color: #8fa0ba; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
  .card .val { font-size: 22px; font-weight: 800; color: #ffffff; }
  .card .sub { font-size: 11px; color: #00f2fe; margin-top: 3px; font-weight: 500; }
  .card.highlight { border-color: #00f2fe; background: #0e2238; }
  .card.highlight .val { color: #00f2fe; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; margin-bottom: 14px; }
  th { background: #161e30; color: #94a3b8; text-align: left; padding: 10px 12px; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase; border-bottom: 1px solid #25314a; }
  td { padding: 10px 12px; border-bottom: 1px solid #1a2236; color: #cbd5e1; }
  tr:nth-child(even) { background: #111724; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
  .badge-cyan { background: rgba(0,242,254,0.15); color: #00f2fe; border: 1px solid rgba(0,242,254,0.3); }
  .badge-green { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
  .badge-gold { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
  .block { background: #141a29; border-left: 3px solid #00f2fe; border-radius: 4px; padding: 14px 18px; margin-bottom: 12px; }
  .block.gold { border-left-color: #f59e0b; }
  .block.green { border-left-color: #10b981; }
  .block-title { font-size: 13px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
  .block-desc { font-size: 12px; color: #94a3b8; line-height: 1.6; }
  .footer { padding: 24px 36px; text-align: center; background: #090c12; font-size: 11px; color: #475569; }
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <div class="logo">Antigravity Performance Lab &bull; Marathon Division</div>
    <h1>Master Progress Audit &amp; Strategic Roadmap</h1>
    <div class="subtitle">Athlete: <strong>Max Sotelo</strong> &nbsp;|&nbsp; Cycle: 2026 Marathon Buildup &nbsp;|&nbsp; Report Date: Sep 03, 2026</div>
  </div>

  <div class="section">
    <div class="section-title">1. High-Level Transformation Matrix (June 2026 Baseline vs. Today)</div>
    <table>
      <thead>
        <tr>
          <th>Metric</th>
          <th>June 2026 (Base)</th>
          <th>July 2026 (Ramp)</th>
          <th>Current (Sep 2026)</th>
          <th>Net Progress</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Body Weight</strong></td>
          <td>74.40 kg</td>
          <td>71.50 kg</td>
          <td><strong style="color:#00f2fe;">68.65 kg</strong></td>
          <td><span class="badge badge-green">-5.75 kg (-12.7 lbs) 🔥</span></td>
        </tr>
        <tr>
          <td><strong>VO2 Max (Garmin)</strong></td>
          <td>54.5 mL/kg</td>
          <td>57.0 mL/kg</td>
          <td><strong style="color:#00f2fe;">58.0 mL/kg</strong></td>
          <td><span class="badge badge-cyan">All-Time High (Top 1%) 🏆</span></td>
        </tr>
        <tr>
          <td><strong>Resting HR</strong></td>
          <td>~50 bpm</td>
          <td>~43 bpm</td>
          <td><strong style="color:#00f2fe;">36 &ndash; 37 bpm</strong></td>
          <td><span class="badge badge-green">-14 bpm Stroke Volume Expansion</span></td>
        </tr>
        <tr>
          <td><strong>5k Threshold Pace</strong></td>
          <td>5:20 /km</td>
          <td>4:55 /km</td>
          <td><strong style="color:#00f2fe;">4:27 /km (22:16 split)</strong></td>
          <td><span class="badge badge-cyan">-53s /km Speed Breakthrough!</span></td>
        </tr>
        <tr>
          <td><strong>Weekly Volume</strong></td>
          <td>25&ndash;30 km/wk</td>
          <td>38&ndash;45 km/wk</td>
          <td><strong style="color:#00f2fe;">48&ndash;52 km/wk</strong></td>
          <td><span class="badge badge-gold">+65% Aerobic Capacity Growth</span></td>
        </tr>
        <tr>
          <td><strong>Ground Contact Time</strong></td>
          <td>~280 ms</td>
          <td>~265 ms</td>
          <td><strong style="color:#00f2fe;">243 ms</strong></td>
          <td><span class="badge badge-green">Elite Elastic Tendon Recoil</span></td>
        </tr>
        <tr>
          <td><strong>Career 20k+ / HMs</strong></td>
          <td>16 completed</td>
          <td>18 completed</td>
          <td><strong style="color:#00f2fe;">20 completed</strong></td>
          <td><span class="badge badge-cyan">24.0k &amp; 22.0k Banked</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="section">
    <div class="section-title">2. Wednesday 10.59 km Speed Anchor &amp; VO2Max Audit</div>
    <div class="grid-4">
      <div class="card highlight">
        <div class="label">Total Distance / Moving Time</div>
        <div class="val">10.59 km</div>
        <div class="sub">47m 48s @ 4:31/km moving avg</div>
      </div>
      <div class="card">
        <div class="label">5k Track Split on Oval</div>
        <div class="val">22m 16s</div>
        <div class="sub">4:27/km avg (Lap 8 kick: 4:08/km!)</div>
      </div>
      <div class="card">
        <div class="label">Aerobic TE / Impulse</div>
        <div class="val">4.7 / 5.0</div>
        <div class="sub">VO2Max Stimulus (TRIMP: 122.0 AU)</div>
      </div>
      <div class="card">
        <div class="label">Mechanical Output</div>
        <div class="val">345 W Avg</div>
        <div class="sub">672W Peak Power | 243ms GCT</div>
      </div>
    </div>
    <div class="block gold">
      <div class="block-title">Why Your Heart Rate Spiked Early in the Warmup:</div>
      <div class="block-desc">
        1. <strong>Starting Mechanical Power:</strong> Outputted 359W @ 5:27/km by second 30 and 364W @ 4:56/km by minute 3 (running Zone 2/Tempo on the road rather than an easy 6:40/km ramp).<br>
        2. <strong>Outdoor Heat Index:</strong> 29&deg;C + 70% RH (Feels like 37.6&deg;C) caused immediate peripheral vasodilation (+15&ndash;20 bpm cardiac drift).<br>
        3. <strong>Active Digestion:</strong> Blood flow shunted between digestive absorption (hashbrown/orange) and leg muscles.<br>
        4. <strong>The Grit:</strong> Despite redlining early, you held 185&ndash;194 bpm for 30 minutes and still dropped a 4:08/km finishing kick!
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">3. Nutrition &amp; Caloric Deficit Status (&le; 67.0 kg Target)</div>
    <div class="grid-2">
      <div class="card">
        <div class="label">Wednesday Closed Ledger (Sep 2)</div>
        <div class="val">-517 kcal</div>
        <div class="sub">Burned: 2,983 kcal | Consumed: 2,466 kcal</div>
      </div>
      <div class="card highlight">
        <div class="label">Weight Progress To Floor</div>
        <div class="val">68.65 kg</div>
        <div class="sub">Only 1.65 kg remaining to 67.0 kg floor!</div>
      </div>
    </div>
    <p style="font-size:12px; color:#94a3b8;">
      &bull; <strong>Week 10 Closed Total Deficit:</strong> <code>-2,850 KCAL</code> (7-for-7 days in a clean deficit).<br>
      &bull; <strong>Post-Run Fueling Strategy:</strong> Your 1,048 kcal Spicy Tuna &amp; Egg Pasta meal delivered 53g protein and 99g carbs right into recovering fibers while maintaining a massive half-thousand calorie deficit!
    </p>
  </div>

  <div class="section">
    <div class="section-title">4. The Strategic Evolution of Tendon &amp; Leg Plyometrics</div>
    <div class="block green">
      <div class="block-title">Why Heavy Leg Weights Were Benched (And What Comes Next):</div>
      <div class="block-desc">
        During July and August, your <strong>22&ndash;24 km long runs absorbed over 350,000 kg of ground impact</strong>, acting as the primary plyometric stimulus while protecting your Achilles from post-gym flare-ups and allowing -5.75 kg of fat loss.<br><br>
        <strong>The Next Phase (10-Min Micro-Dose Tendon Armor):</strong><br>
        &bull; <strong>Pogo Hops (Ankle Spring):</strong> 3 &times; 25 reps (Sharpens 240ms ground contact time).<br>
        &bull; <strong>Eccentric Single-Leg Heel Drops:</strong> 3 &times; 15 reps (Tendon collagen alignment).<br>
        &bull; <strong>Bulgarian Split Squats (Bodyweight):</strong> 3 &times; 8&ndash;10 reps (Glute/pelvic stability).<br>
        &bull; <strong>Tibialis Wall Raises:</strong> 3 &times; 20 reps (Shin splint defense).
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">5. Roadmap for Week 11 &amp; The Journey to the 30k Monster Long Run</div>
    <div class="block">
      <div class="block-title">Week 11 Remaining Schedule:</div>
      <div class="block-desc">
        &bull; <strong>Thursday (Today, Sep 3):</strong> Hydrostatic Pool Recovery (1,000&ndash;1,200m) or Pure Rest (0.0 km).<br>
        &bull; <strong>Friday (Sep 4):</strong> 6.0 &ndash; 7.0 km Zone 2 Aerobic Base + 4 &times; 80m Strides.<br>
        &bull; <strong>Saturday (Sep 5):</strong> 4.0 &ndash; 5.0 km Zone 1 Easy Shakeout + Glycogen Reload Dinner.<br>
        &bull; <strong>Sunday (Sep 6):</strong> 24.0 &ndash; 25.0 km Peak Build I Long Run (Career HM #21!).
      </div>
    </div>
    <div class="block gold">
      <div class="block-title">Upcoming Long Run Step-Wave Escalation Map:</div>
      <div class="block-desc">
        &bull; <strong>Week 11 (This Sun, Sep 06):</strong> 24.0 &ndash; 25.0 km (Solidify 25 km barrier).<br>
        &bull; <strong>Week 12 (Sun, Sep 13):</strong> 26.0 &ndash; 27.0 km (New Cycle High Distance Peak!).<br>
        &bull; <strong>Week 13 (Sun, Sep 20):</strong> 21.0 &ndash; 22.0 km (Consolidation Step-Down).<br>
        &bull; <strong>Week 14 (Sun, Sep 27):</strong> 28.0 &ndash; 30.0 km (THE 30K MONSTER MILESTONE!).<br>
        &bull; <strong>Week 15 (Sun, Oct 04):</strong> 30.0 &ndash; 32.0 km (Peak Race Simulation).
      </div>
    </div>
  </div>

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
print('SUCCESSFULLY SENT AUDIT EMAIL TO:', TO_EMAIL)
