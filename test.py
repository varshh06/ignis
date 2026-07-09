"""
Run this from inside your boiler-website folder (same place as .env and app.py):
    python check_env.py

It loads .env exactly the way app.py does, then shows you exactly what
Flask is actually seeing - including any invisible characters - and tries
the real SMTP login with those exact values.
"""
import os
import smtplib
import ssl
from dotenv import load_dotenv

load_dotenv()

sender = os.environ.get("SENDER_EMAIL")
password = os.environ.get("SENDER_APP_PASSWORD")
admin = os.environ.get("ADMIN_EMAIL")
smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
smtp_port = int(os.environ.get("SMTP_PORT", 587))

print("---- What app.py is actually reading from .env ----")
print("SENDER_EMAIL   :", repr(sender))
print("SENDER_APP_PASSWORD:", repr(password), f"(length={len(password) if password else 0})")
print("ADMIN_EMAIL    :", repr(admin))
print("SMTP_SERVER    :", repr(smtp_server))
print("SMTP_PORT      :", repr(smtp_port))
print("----------------------------------------------------")

if not (sender and password and admin):
    print("PROBLEM FOUND: one or more values is None/empty - .env is not being")
    print("loaded, or the file isn't in this folder, or a variable name is misspelled.")
else:
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender, password)
        print("SUCCESS: login worked using the exact values from your .env file.")
    except smtplib.SMTPAuthenticationError as e:
        print("LOGIN FAILED with the values above:", e)
    except Exception as e:
        print("OTHER ERROR:", e)