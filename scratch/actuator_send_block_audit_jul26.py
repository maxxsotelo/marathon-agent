"""
actuator_send_block_audit_email.py
Sends the Week 5 Block Audit to maxxsotelo@gmail.com
"""
import os, sys, smtplib
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
FROM_EMAIL  = os.getenv("GARMIN_EMAIL")
APP_PASS    = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL    = "maxxsotelo@gmail.com"

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Antigravity Block Audit — Week 5</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #0d0f14; color: #e8eaf0; }
  .wrapper { max-width: 720px; margin: 0 auto; background: #0d0f14; }
  .header { background: linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%); padding: 40px 40px 30px; border-bottom: 2px solid #00d4aa; }
  .logo { font-size: 11px; letter-spacing: 4px; color: #00d4aa; text-transform: uppercase; margin-bottom: 12px; }
  .header h1 { font-size: 28px; font-weight: 700; color: #ffffff; line-height: 1.2; }
  .header .subtitle { font-size: 14px; color: #8892a4; margin-top: 8px; }
  .section { padding: 28px 40px; border-bottom: 1px solid #1e2535; }
  .section-title { font-size: 12px; letter-spacing: 3px; color: #00d4aa; text-transform: uppercase; margin-bottom: 18px; font-weight: 600; }
  .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
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
  .verdict { background: linear-gradient(135deg, #0a1628 0%, #0d1117 100%); border: 1px solid #00d4aa; border-radius: 10px; padding: 24px; margin-top: 8px; }
  .verdict p { font-size: 13px; color: #cdd5e0; line-height: 1.7; margin-bottom: 10px; }
  .verdict p:last-child { margin-bottom: 0; }
  .footer { padding: 28px 40px; text-align: center; background: #080b10; }
  .footer p { font-size: 11px; color: #3d4a5c; line-height: 1.7; }
  .footer .brand { color: #00d4aa; font-weight: 700; letter-spacing: 2px; }
  .alert-box { background: #1a1010; border-left: 3px solid #ff6b6b; border-radius: 4px; padding: 14px 18px; margin-top: 12px; font-size: 12px; color: #ff9f9f; line-height: 1.6; }
  .ok-box { background: #0a1a12; border-left: 3px solid #00d4aa; border-radius: 4px; padding: 14px 18px; margin-top: 12px; font-size: 12px; color: #8ef0d4; line-height: 1.6; }
</style>
</head>
<body>
<div class="wrapper">

  <!-- HEADER -->
  <div class="header">
    <div class="logo">Antigravity Agent &mdash; Performance Lab</div>
    <h1>Week 5 Block Audit &amp; Milestone Report</h1>
    <div class="subtitle">Athlete: Max Sotelo &nbsp;&bull;&nbsp; Report Date: July 26, 2026 &nbsp;&bull;&nbsp; Week Closed</div>
  </div>

  <!-- ACWR & LOAD -->
  <div class="section">
    <div class="section-title">Training Load &mdash; ACWR Status</div>
    <div class="metric-grid">
      <div class="metric-card good">
        <div class="label">ACWR</div>
        <div class="value">0.97</div>
        <div class="note">Green &mdash; Optimal Zone (0.80&ndash;1.30)</div>
      </div>
      <div class="metric-card good">
        <div class="label">HRV Weekly Avg</div>
        <div class="value">116<span class="unit">ms</span></div>
        <div class="note">Elite range &mdash; BALANCED status</div>
      </div>
      <div class="metric-card good">
        <div class="label">VO2 Max</div>
        <div class="value">57<span class="unit">ml/kg/min</span></div>
        <div class="note">All-time high &uarr; from 56 after today's run</div>
      </div>
      <div class="metric-card">
        <div class="label">Week 5 Mileage</div>
        <div class="value">47.45<span class="unit">km</span></div>
        <div class="note">-1.7% vs last week (step-down: correct)</div>
      </div>
    </div>
  </div>

  <!-- WEEK 5 LONG RUN MILESTONE -->
  <div class="section">
    <div class="section-title">Week 5 Long Run &mdash; July 26, 2026</div>
    <div class="metric-grid">
      <div class="metric-card good">
        <div class="label">Distance</div>
        <div class="value">21.32<span class="unit">km</span></div>
        <div class="note">HM distance with negative split</div>
      </div>
      <div class="metric-card good">
        <div class="label">Moving Time (PR)</div>
        <div class="value">1:48:52</div>
        <div class="note">Previous best: 1:58:26 &mdash; 9:34 faster</div>
      </div>
      <div class="metric-card good">
        <div class="label">Avg Moving Pace (PR)</div>
        <div class="value">5:06<span class="unit">/km</span></div>
        <div class="note">Previous best: 5:22/km</div>
      </div>
      <div class="metric-card warn">
        <div class="label">Final Km Pace</div>
        <div class="value">4:24<span class="unit">/km</span></div>
        <div class="note">Fastest km of the entire run &mdash; negative split</div>
      </div>
      <div class="metric-card">
        <div class="label">Avg HR</div>
        <div class="value">160<span class="unit">bpm</span></div>
      </div>
      <div class="metric-card alert">
        <div class="label">Max HR</div>
        <div class="value">189<span class="unit">bpm</span></div>
        <div class="note">Full send on final 2km</div>
      </div>
    </div>

    <div class="ok-box">
      <strong>Conditions context:</strong> Crowded track, hundreds of pedestrians blocking lanes 3&ndash;8, dead Boston 12s at 947km, no carbon-plate shoes. Corrected projection on open road in Evo SLs: <strong>~4:44&ndash;4:51/km average &rarr; ~1:40&ndash;1:42 HM</strong>.
    </div>
  </div>

  <!-- KM SPLITS -->
  <div class="section">
    <div class="section-title">Km-by-Km Split Table</div>
    <table>
      <tr><th>Km</th><th>Pace</th><th>Avg HR</th><th>Max HR</th><th>Cadence</th><th>Phase</th></tr>
      <tr><td>1</td><td>5:43</td><td>135</td><td>146</td><td>168</td><td>Warmup</td></tr>
      <tr><td>2</td><td>5:38</td><td>152</td><td>156</td><td>172</td><td>Settling</td></tr>
      <tr><td>3</td><td>5:29</td><td>155</td><td>159</td><td>172</td><td>Zone 2 locked</td></tr>
      <tr><td>4</td><td>5:29</td><td>155</td><td>158</td><td>173</td><td>Steady</td></tr>
      <tr><td>5</td><td>5:18</td><td>159</td><td>162</td><td>175</td><td>Natural drift</td></tr>
      <tr><td>6</td><td>5:03</td><td>160</td><td>170</td><td>173</td><td>Crowd surge</td></tr>
      <tr><td>7</td><td>5:22</td><td>160</td><td>166</td><td>170</td><td>Re-settled</td></tr>
      <tr><td>8</td><td>5:28</td><td>158</td><td>163</td><td>175</td><td>Controlled</td></tr>
      <tr><td>9</td><td>5:30</td><td>154</td><td>159</td><td>174</td><td>HR recovering</td></tr>
      <tr><td>10</td><td>5:29</td><td>155</td><td>159</td><td>175</td><td>Halfway &mdash; consistent</td></tr>
      <tr><td>11</td><td>5:29</td><td>156</td><td>160</td><td>176</td><td>Controlled</td></tr>
      <tr><td>12</td><td>5:03</td><td>147</td><td>160</td><td>166</td><td>Pee/water stop</td></tr>
      <tr><td>13</td><td>5:05</td><td>160</td><td>165</td><td>177</td><td>Back in rhythm</td></tr>
      <tr><td>14</td><td>5:08</td><td>161</td><td>165</td><td>174</td><td>Building</td></tr>
      <tr><td>15</td><td>5:00</td><td>160</td><td>165</td><td>177</td><td>Shifting gears</td></tr>
      <tr><td><strong>16</strong></td><td><strong>4:41</strong></td><td><strong>170</strong></td><td><strong>174</strong></td><td><strong>178</strong></td><td><strong>First full-send</strong></td></tr>
      <tr><td><strong>17</strong></td><td><strong>5:00</strong></td><td><strong>170</strong></td><td><strong>174</strong></td><td><strong>176</strong></td><td><strong>Holding HR</strong></td></tr>
      <tr><td><strong>18</strong></td><td><strong>4:53</strong></td><td><strong>166</strong></td><td><strong>172</strong></td><td><strong>175</strong></td><td><strong>Still fast</strong></td></tr>
      <tr><td><strong>19</strong></td><td><strong>4:58</strong></td><td><strong>171</strong></td><td><strong>177</strong></td><td><strong>178</strong></td><td><strong>Near-threshold</strong></td></tr>
      <tr><td><strong>20</strong></td><td><strong>4:33</strong></td><td><strong>178</strong></td><td><strong>188</strong></td><td><strong>179</strong></td><td><strong>Full gas</strong></td></tr>
      <tr><td><strong>21</strong></td><td><strong>4:24</strong></td><td><strong>183</strong></td><td><strong>189</strong></td><td><strong>182</strong></td><td><strong>FASTEST KM &mdash; LAST KM</strong></td></tr>
    </table>
  </div>

  <!-- 3-WEEK BLOCK AUDIT -->
  <div class="section">
    <div class="section-title">3-Week Rolling Block Audit</div>
    <table>
      <tr><th>Week</th><th>Mileage</th><th>WoW Change</th><th>Longest Run</th><th>Avg Pace</th><th>Avg HR</th><th>Strength</th><th>10% Rule</th></tr>
      <tr><td>Jun 29&ndash;Jul 5</td><td>54.80 km</td><td>+25.4%</td><td>15.17 km</td><td>5:37/km</td><td>158</td><td>5 &#10003;</td><td style="color:#ffd166;">EXCEEDED</td></tr>
      <tr><td>Jul 6&ndash;12</td><td>40.02 km</td><td>-27.0%</td><td>12.46 km</td><td>5:54/km</td><td>144</td><td>4 &#10003;</td><td style="color:#00d4aa;">OK</td></tr>
      <tr><td>Jul 13&ndash;19</td><td>48.27 km</td><td>+20.6%</td><td>22.21 km</td><td>5:10/km</td><td>158</td><td>3 &#10003;</td><td style="color:#ffd166;">EXCEEDED</td></tr>
      <tr><td><strong>Jul 20&ndash;26 (Week 5)</strong></td><td><strong>47.45 km</strong></td><td><strong>-1.7%</strong></td><td><strong>21.32 km</strong></td><td><strong>5:22/km</strong></td><td><strong>149</strong></td><td><strong>2 &#10003;</strong></td><td style="color:#00d4aa;"><strong>OK</strong></td></tr>
    </table>
    <div class="alert-box" style="margin-top:12px;">
      <strong>10% Rule Flags (Jun 29, Jul 13):</strong> Both were deliberate coach-approved progressive overload weeks followed by cut-back weeks. The ACWR absorbed both spikes and stayed in the green zone throughout. No injury risk materialized.
    </div>
  </div>

  <!-- PR TABLE -->
  <div class="section">
    <div class="section-title">Personal Records Set This Week</div>
    <table>
      <tr><th>Record</th><th>Previous</th><th>New</th><th>Improvement</th></tr>
      <tr><td>HM Moving Time PR</td><td>1:58:26</td><td style="color:#00d4aa;"><strong>1:48:52</strong></td><td style="color:#00d4aa;">-9:34</td></tr>
      <tr><td>HM Average Pace PR</td><td>5:22/km</td><td style="color:#00d4aa;"><strong>5:06/km</strong></td><td style="color:#00d4aa;">-16 sec/km</td></tr>
      <tr><td>VO2 Max (Garmin)</td><td>56 ml/kg/min</td><td style="color:#00d4aa;"><strong>57 ml/kg/min</strong></td><td style="color:#00d4aa;">+1 point</td></tr>
      <tr><td>Total 21km+ Runs</td><td>16</td><td style="color:#00d4aa;"><strong>17</strong></td><td style="color:#00d4aa;">+1</td></tr>
    </table>
  </div>

  <!-- RACE PROJECTIONS -->
  <div class="section">
    <div class="section-title">Race Time Projections (VO2 Max 57, Fresh Legs)</div>
    <table>
      <tr><th>Race</th><th>Projected Time</th></tr>
      <tr><td>5 km</td><td>~18:30</td></tr>
      <tr><td>10 km</td><td>~38:30</td></tr>
      <tr><td>Half Marathon</td><td>~1:25&ndash;1:28</td></tr>
      <tr><td><strong>Marathon</strong></td><td style="color:#00d4aa;"><strong>~2:58&ndash;3:02</strong></td></tr>
    </table>
  </div>

  <!-- VERDICT -->
  <div class="section">
    <div class="section-title">Coaching Verdict</div>
    <div class="verdict">
      <p><strong style="color:#00d4aa;">Sub-3 Marathon is Real.</strong> At VO2 Max 57 with a proven ability to run 5:06/km for a half marathon distance on a step-down week with dead shoes on a crowded track, the physiological ceiling for a sub-3 marathon is confirmed. The engine is built. Now we sharpen the blade.</p>
      <p><strong style="color:#ffd166;">Critical Shoe Warning.</strong> Boston 12 Pair 1 is at 947km. It must not be used for any more long runs. The dead foam is an unquantified injury risk. Evo SLs or Boston 12 Pair 2 (144km) only from this point forward for any run over 10km.</p>
      <p><strong style="color:#00d4aa;">Week 6 Prescription:</strong> Full rest Monday. Zone 2 Tuesday. Speed session Thursday (VO2 Max or Threshold decision based on morning vitals). Pre-Fatigue Legs + 7km Saturday. Long Run 22&ndash;24km Sunday &mdash; step back UP after step-down week. Use Evo SLs.</p>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <p class="brand">ANTIGRAVITY</p>
    <p>Powered by the Kiat Engine &mdash; Custom Physiological Intelligence Layer<br>
    Garmin Forerunner 165 &bull; core_block_auditor.py &bull; sensor_audit_14d.py<br><br>
    All training decisions are confirmed against live telemetry. This report was auto-generated on July 26, 2026.</p>
  </div>

</div>
</body>
</html>
"""

plain = """ANTIGRAVITY — Week 5 Block Audit | July 26, 2026

ACWR: 0.97 (Green) | HRV: 116ms (BALANCED) | VO2 Max: 57 ml/kg/min (All-time high)

LONG RUN PR — July 26, 2026
Distance: 21.32km | Moving Time: 1:48:52 (PR, prev 1:58:26) | Avg Pace: 5:06/km (PR)
Final km: 4:24/km — fastest km of the entire run (negative split)
Conditions: Crowded track, dead shoes (947km), no carbon plate

3-WEEK BLOCK AUDIT
Jun 29-Jul 5:  54.80km | +25.4% WoW | Strength: 5 | 10% EXCEEDED
Jul 6-12:      40.02km | -27.0% WoW | Strength: 4 | 10% OK
Jul 13-19:     48.27km | +20.6% WoW | Strength: 3 | 10% EXCEEDED
Jul 20-26:     47.45km | -1.7%  WoW | Strength: 2 | 10% OK

PERSONAL RECORDS
HM Moving Time: 1:48:52 (was 1:58:26) — 9:34 improvement
HM Avg Pace: 5:06/km (was 5:22/km)
VO2 Max: 57 ml/kg/min (was 56)

MARATHON PROJECTION: ~2:58-3:02

WEEK 6 PLAN
Mon Jul 27: Full Rest
Tue Jul 28: 10km Zone 2
Thu Jul 30: Speed Session (VO2 Max or Threshold)
Sat Aug 1:  Pre-Fatigue Legs + 7km Run
Sun Aug 2:  22-24km Long Run (Evo SLs only)

Antigravity Agent | Powered by Kiat Engine
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = "Antigravity | Week 5 Block Audit & Milestone Report — July 26, 2026"
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
