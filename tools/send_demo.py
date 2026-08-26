import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.settings import load_settings

from email.message import EmailMessage
from email.utils import formataddr

s = load_settings()
primary = s.accounts[0]

demo = EmailMessage()
demo["From"] = formataddr(("MailPilot Demo", primary.address))
demo["To"] = primary.address
demo["Subject"] = "MailPilot demo - clean card format"
body = (
    "Hi Steven,\n\n"
    "This is the live demonstration of your new alert structure.\n"
    "Notice the attachment listed below, and the clean layout:\n"
    "From / To / Title / Time / Attachment / Message.\n\n"
    "- MailPilot"
)
demo.set_content(body)
demo.add_attachment(
    b"MailPilot demo attachment - if you can read this, attachment detection works.",
    maintype="text", subtype="plain", filename="demo-note.txt",
)

import smtplib
with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
    server.login(primary.address, primary.password)
    server.sendmail(primary.address, [primary.address], demo.as_string())
print("DEMO EMAIL SENT ->", primary.address)
