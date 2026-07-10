"""
Ignis Boiler Works — Flask backend
-----------------------------------
Routes:
    GET  /                     Home
    GET  /services             Services list
    GET  /services/<slug>      Individual service landing page
    GET  /gallery              Gallery
    GET  /contact              Contact page
    GET  /enquiry              Enquiry form (also generates captcha)
    POST /enquiry              Handles submission -> Postgres + email
    GET  /captcha/refresh      Returns a fresh captcha question (AJAX)
"""

import os
import traceback
import resend

import psycopg2 # type: ignore
import psycopg2.extras # type: ignore
import requests
from dotenv import load_dotenv # type: ignore
from flask import ( # type: ignore
    Flask, render_template, request, redirect,
    url_for, flash, session
)

load_dotenv()
resend.api_key = os.environ.get("RESEND_API_KEY")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

DATABASE_URL = os.environ.get("DATABASE_URL")

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


# ------------------------------------------------------------------
# DB helpers
# ------------------------------------------------------------------
def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def fetch_services():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM services ORDER BY display_order ASC")
        rows = cur.fetchall()
    conn.close()
    return rows


def fetch_service_by_slug(slug):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM services WHERE slug = %s", (slug,))
        row = cur.fetchone()
    conn.close()
    return row


def fetch_gallery():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM gallery ORDER BY display_order ASC")
        rows = cur.fetchall()
    conn.close()
    return rows


def insert_enquiry(name, email, phone, service, message):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            """INSERT INTO enquiries (name, email, phone, service, message)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (name, email, phone, service, message),
        )
        new_id = cur.fetchone()["id"]
    conn.commit()
    conn.close()
    return new_id


def mark_email_sent(enquiry_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE enquiries SET email_sent = TRUE WHERE id = %s", (enquiry_id,))
    conn.commit()
    conn.close()


# ------------------------------------------------------------------
# CAPTCHA (Google reCAPTCHA v2 "I'm not a robot" checkbox)
# ------------------------------------------------------------------
def verify_recaptcha(token, remote_ip=None):
    if not RECAPTCHA_SECRET_KEY:
        app.logger.warning("RECAPTCHA_SECRET_KEY not set - skipping verification (dev mode)")
        return True
    if not token:
        return False
    try:
        resp = requests.post(
            RECAPTCHA_VERIFY_URL,
            data={"secret": RECAPTCHA_SECRET_KEY, "response": token, "remoteip": remote_ip},
            timeout=6,
        )
        result = resp.json()
        return bool(result.get("success"))
    except Exception as e:
        app.logger.error(f"reCAPTCHA verification failed: {e}")
        return False


# ------------------------------------------------------------------
# Email
# ------------------------------------------------------------------
def send_enquiry_email(name, email, phone, service, message):
    try:
        resend.Emails.send({
            "from": "Ignis Website <onboarding@resend.dev>",
            "to": [ADMIN_EMAIL],
            "subject": f"New Enquiry - {name}",
            "text": f"""
New enquiry received.

Name: {name}
Email: {email}
Phone: {phone}
Service: {service}

Message:
{message}
"""
        })

        return True

    except Exception as e:
        app.logger.error(f"Resend Error: {e}")
        return False
# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.route("/")
def home():
    services = fetch_services()
    return render_template("index.html", services=services, active="home")


@app.route("/services")
def services():
    all_services = fetch_services()
    return render_template("services.html", services=all_services, active="services")


@app.route("/services/<slug>")
def service_detail(slug):
    service = fetch_service_by_slug(slug)
    if not service:
        return redirect(url_for("services"))
    return render_template("service_detail.html", service=service, active="services")


@app.route("/gallery")
def gallery():
    images = fetch_gallery()
    categories = sorted({row["category"] for row in images})
    return render_template("gallery.html", images=images, categories=categories, active="gallery")


@app.route("/contact")
def contact():
    return render_template("contact.html", active="contact")


@app.route("/enquiry", methods=["GET", "POST"])
def enquiry():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        service = request.form.get("service", "").strip()
        message = request.form.get("message", "").strip()
        recaptcha_token = request.form.get("g-recaptcha-response", "")

        errors = []
        if not name or len(name) < 2:
            errors.append("Please enter your full name.")
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address.")
        if not phone or len(phone) < 7:
            errors.append("Please enter a valid phone number.")
        if not message or len(message) < 10:
            errors.append("Please describe your requirement in a few more words.")

        if not verify_recaptcha(recaptcha_token, request.remote_addr):
            errors.append("Please complete the 'I'm not a robot' verification.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template(
                "enquiry.html",
                active="enquiry",
                services=fetch_services(),
                recaptcha_site_key=RECAPTCHA_SITE_KEY,
                form_data=request.form,
            )

        enquiry_id = insert_enquiry(name, email, phone, service, message)
        sent = send_enquiry_email(name, email, phone, service, message)
        if sent:
            mark_email_sent(enquiry_id)
            flash("Thank you — your enquiry has been submitted and our team has been notified by email.", "success")
        else:
            flash("Your enquiry was saved. (Email notification could not be sent — check server mail config.)", "success")

        return redirect(url_for("enquiry"))

    return render_template(
        "enquiry.html",
        active="enquiry",
        services=fetch_services(),
        recaptcha_site_key=RECAPTCHA_SITE_KEY,
        form_data={},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
