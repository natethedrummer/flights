"""
Send HTML email alerts for flight deals via SMTP.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import config

log = logging.getLogger(__name__)


def send_deal_alert(depart_date: date, return_date: date,
                    per_person_price: float, total_price: float,
                    reason: str):
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        log.warning("SMTP credentials not configured — skipping email")
        return

    subject = (
        f"✈️ Flight Deal! MSP→DFW ${per_person_price:.0f}/person "
        f"({depart_date.strftime('%b %d')}–{return_date.strftime('%b %d')})"
    )

    html = f"""\
<html><body style="font-family: -apple-system, sans-serif; max-width: 500px;">
<h2 style="color: #1a73e8;">Flight Deal Alert</h2>
<table style="border-collapse: collapse; width: 100%;">
  <tr><td style="padding: 8px; font-weight: bold;">Route</td>
      <td style="padding: 8px;">MSP → DFW (nonstop, Delta)</td></tr>
  <tr style="background: #f8f9fa;">
      <td style="padding: 8px; font-weight: bold;">Depart</td>
      <td style="padding: 8px;">{depart_date.strftime('%A, %B %d, %Y')}</td></tr>
  <tr><td style="padding: 8px; font-weight: bold;">Return</td>
      <td style="padding: 8px;">{return_date.strftime('%A, %B %d, %Y')}</td></tr>
  <tr style="background: #f8f9fa;">
      <td style="padding: 8px; font-weight: bold;">Price</td>
      <td style="padding: 8px; color: #0d904f; font-size: 1.2em; font-weight: bold;">
        ${per_person_price:.0f}/person · ${total_price:.0f} total (4 passengers)
      </td></tr>
  <tr><td style="padding: 8px; font-weight: bold;">Why it's a deal</td>
      <td style="padding: 8px;">{reason}</td></tr>
</table>
<p style="color: #666; font-size: 0.85em; margin-top: 20px;">
  Sent by Flight Deal Monitor · MSP→DFW for ISD 833 school breaks
</p>
</body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_USER
    msg["To"] = config.ALERT_TO
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, config.ALERT_TO, msg.as_string())
        log.info("Alert email sent to %s", config.ALERT_TO)
    except Exception:
        log.exception("Failed to send email")
