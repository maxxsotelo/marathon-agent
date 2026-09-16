"""
send_audit_email.py
"""
import os, sys, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
FROM_EMAIL  = os.getenv("GARMIN_EMAIL")
APP_PASS    = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL    = "maxxsotelo@gmail.com"

# Read the artifact
audit_path = r"C:\Users\Max\.gemini\antigravity\brain\3a089547-6db7-486f-9c49-05bc442734f2\artifacts\block_audit_aug12.md"
with open(audit_path, "r", encoding="utf-8") as f:
    audit_md = f.read()

html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
  body {{ font-family: 'Courier New', Courier, monospace; background: #ffffff; color: #333333; padding: 20px; }}
  pre {{ white-space: pre-wrap; }}
</style>
</head>
<body>
<pre>
{audit_md}
</pre>
</body>
</html>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = "Antigravity Block Audit: Week 8 Deload (Aug 12, 2026)"
msg["From"]    = f"Antigravity Coach <{FROM_EMAIL}>"
msg["To"]      = TO_EMAIL

msg.attach(MIMEText(audit_md, "plain"))
msg.attach(MIMEText(html, "html"))

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(FROM_EMAIL, APP_PASS)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
    print("[OK] Audit emailed to", TO_EMAIL)
except Exception as e:
    print("[ERROR]", e)
