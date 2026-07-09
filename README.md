# Ignis Boiler Works — Website

A 5-page boiler company website (Home, Services + per-service landing pages, Gallery, Contact, Enquiry) built with **Flask** and **PostgreSQL**, featuring self-hosted CAPTCHA protection and email notifications on form submission.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [1. Database Setup](#1-database-setup)
- [2. Project Setup](#2-project-setup)
- [3. Email Notification Setup](#3-email-notification-setup)
- [4. Running the App](#4-running-the-app)
- [5. How It Works](#5-how-it-works)
- [6. Managing Content](#6-managing-content)
- [7. Production Checklist](#7-production-checklist)

---

## Project Structure

```
boiler-website/
├── app.py              # Flask backend (routes, DB, captcha, email)
├── schema.sql           # PostgreSQL schema + seed data (services & gallery)
├── requirements.txt
├── .env.example          # Copy to .env and fill in real values
├── templates/            # Jinja2 HTML templates (5 pages + base + service detail)
└── static/
    ├── css/style.css
    ├── js/main.js
    └── img/
```

## Prerequisites

- Python 3.x
- PostgreSQL
- A Gmail (or other SMTP) account for outgoing notifications
- A Google reCAPTCHA v2 key pair

---

## 1. Database Setup

### Install PostgreSQL

| OS            | Command                                                                      |
| ------------- | ---------------------------------------------------------------------------- |
| Windows / Mac | Install from [postgresql.org/download](https://www.postgresql.org/download/) |
| Linux         | `sudo apt install postgresql`                                                |

### Create the Database

From a terminal:

```bash
psql -U postgres
```

Inside the `psql` prompt:

```sql
CREATE DATABASE boiler_db;
\q
```

### Load Schema and Seed Data

```bash
psql -U postgres -d boiler_db -f schema.sql
```

This creates three tables:

| Table       | Purpose                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------ |
| `enquiries` | Every form submission (name, email, phone, service, message, timestamp, email-sent status) |
| `services`  | The service catalogue shown on the Services page (editable directly in the DB)             |
| `gallery`   | Gallery images with category tags, shown dynamically                                       |

---

## 2. Project Setup

```bash
cd boiler-website
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/boiler_db
SECRET_KEY=some-long-random-string
```

---

## 3. Email Notification Setup

It's recommended to use a **throwaway Gmail account** for testing (e.g. `ignisboilertest@gmail.com`) rather than a real company inbox.

1. Create the Gmail account (or use an existing test one).
2. Go to **Google Account → Security → 2-Step Verification** and enable it (required for App Passwords).
3. Go to **Security → App Passwords**, choose app **"Mail"**, and generate a 16-character password.
4. Add the following to `.env`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=ignisboilertest@gmail.com
SENDER_APP_PASSWORD=the16charapppassword
ADMIN_EMAIL=ignisboilertest@gmail.com
```

> **Note:** `SENDER_EMAIL` sends the mail; `ADMIN_EMAIL` receives it. For testing, they can be the same address. When going live, point `ADMIN_EMAIL` at the real company inbox — `SENDER_EMAIL` can remain a dedicated "no-reply" sending account, which is standard practice.

Any other SMTP provider (Outlook, Zoho, SendGrid, Amazon SES) also works — just update `SMTP_SERVER` / `SMTP_PORT` accordingly.

---

## 4. Running the App

```bash
python app.py
```

Visit **http://localhost:5000**

---

## 5. How It Works

### CAPTCHA (Spam Protection)

Uses Google reCAPTCHA v2 — the "I'm not a robot" checkbox widget.

**Setup:**

1. Go to [google.com/recaptcha/admin/create](https://www.google.com/recaptcha/admin/create)
2. Choose **reCAPTCHA v2 → "I'm not a robot" Checkbox**
3. Under **Domains**, add `localhost` for local testing and your real domain once deployed (multiple domains can share one key).
4. Submit, then copy the Site Key and Secret Key into `.env`:

```env
RECAPTCHA_SITE_KEY=your-site-key
RECAPTCHA_SECRET_KEY=your-secret-key
```

- The **site key** is used client-side (visible in page HTML — this is normal).
- The **secret key** is used server-side in `verify_recaptcha()` in `app.py`, which calls Google's `siteverify` endpoint before an enquiry is accepted.

> **Dev convenience:** If `RECAPTCHA_SECRET_KEY` is left blank, the app logs a warning and allows submissions through unverified — useful for testing the DB/email flow before generating Google keys. **Do not ship to production without real keys.**

### Form Submission Flow

1. User fills out the Enquiry form and completes the captcha.
2. Flask validates the fields and captcha.
3. **On success:** a row is inserted into `enquiries` → an email is sent via SMTP to `ADMIN_EMAIL` → a success message is shown → the `email_sent` flag is updated in the DB.
4. **On failure:** the form re-renders with specific error messages and a fresh captcha.

### Gallery / Services Dynamic Data

Both are pulled from PostgreSQL on every request — content can be added, edited, or removed directly in the `services` and `gallery` tables with no code changes required.

### Images

Gallery and service images currently pull from **LoremFlickr** (`loremflickr.com/WIDTHxHEIGHT/tags`), which serves real, freely-usable stock photos matched to keyword tags — producing realistic industrial/boiler imagery rather than generic placeholders. Replace any `image_url` in the DB (or the seed data in `schema.sql`) with your own hosted photography whenever available; everything else continues to work unchanged.

---

## 6. Managing Content

**Add a new gallery photo:**

```sql
INSERT INTO gallery (title, category, image_url, display_order)
VALUES ('New Site Install', 'Installations', 'https://yourcdn.com/photo.jpg', 9);
```

**Edit a service description:**

```sql
UPDATE services SET full_desc = 'Updated text...' WHERE slug = 'steam-boilers';
```

---

## 7. Production Checklist

- [ ] Replace placeholder phone/address/email in `templates/base.html` and `contact.html`
- [ ] Point `ADMIN_EMAIL` at the real company inbox
- [ ] Replace LoremFlickr URLs with your own photographed images
- [ ] Set `app.run(debug=False)` and use a real WSGI server (e.g. `gunicorn`, `waitress`) in production
- [ ] Add `.env` to `.gitignore` — never commit real credentials
- [ ] Add rate-limiting (e.g. `Flask-Limiter`) on the `/enquiry` POST route in addition to the captcha
