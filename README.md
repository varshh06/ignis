# Ignis Boiler Works — Website

A 5-page boiler company website: Home, Services (+ per-service landing pages),
Gallery, Contact, Enquiry. Flask + PostgreSQL backend, self-hosted CAPTCHA,
and email notification on form submission.

## 1. What's inside

```
boiler-website/
├── app.py              Flask backend (routes, DB, captcha, email)
├── schema.sql           PostgreSQL schema + seed data (services & gallery)
├── requirements.txt
├── .env.example          Copy to .env and fill in real values
├── templates/            Jinja2 HTML templates (5 pages + base + service detail)
└── static/
    ├── css/style.css
    ├── js/main.js
    └── img/
```

## 2. Install PostgreSQL and create the database

**Windows/Mac:** install from https://www.postgresql.org/download/
**Linux:** `sudo apt install postgresql`

Then, from a terminal:

```bash
psql -U postgres
```

Inside the `psql` prompt:

```sql
CREATE DATABASE boiler_db;
\q
```

Load the schema and seed data:

```bash
psql -U postgres -d boiler_db -f schema.sql
```

This creates 3 tables:
- **enquiries** — every form submission (name, email, phone, service, message, timestamp, whether the email send succeeded)
- **services** — the service catalogue shown on the Services page (editable directly in the DB)
- **gallery** — gallery images with category tags, shown dynamically

## 3. Set up the project

```bash
cd boiler-website
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/boiler_db
SECRET_KEY=some-long-random-string
```

## 4. Set up the "dummy" test mailbox for form notifications

Rather than using a real company inbox while testing, create a throwaway Gmail
account purely to receive test enquiries (e.g. `ignisboilertest@gmail.com`).

1. Create the Gmail account (or use an existing test one).
2. Go to **Google Account → Security → 2-Step Verification** and turn it on
   (App Passwords require this).
3. Go to **Security → App Passwords**, choose app "Mail", generate a 16-character password.
4. Put that in `.env`:

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=ignisboilertest@gmail.com
SENDER_APP_PASSWORD=the16charapppassword
ADMIN_EMAIL=ignisboilertest@gmail.com
```

`SENDER_EMAIL` sends the mail, `ADMIN_EMAIL` receives it — for testing they can
be the same address. When you're ready to go live, point `ADMIN_EMAIL` at the
real company inbox (SENDER_EMAIL can stay as a dedicated "no-reply" sending account,
which is standard practice — companies rarely send automated mail from a real
person's inbox).

> If you'd rather not use Gmail, any SMTP provider works (Outlook, Zoho, SendGrid,
> Amazon SES) — just change `SMTP_SERVER`/`SMTP_PORT` accordingly.

## 5. Run it

```bash
python app.py
```

Visit **http://localhost:5000**

## 6. How the pieces fit together

**CAPTCHA (spam protection):** Google reCAPTCHA v2, the "I'm not a robot"
checkbox widget. Setup:

1. Go to https://www.google.com/recaptcha/admin/create
2. Choose **reCAPTCHA v2 → "I'm not a robot" Checkbox**
3. Under "Domains", add `localhost` for local testing, and your real domain
   once you deploy (you can list multiple domains on one key — add both now).
4. Submit, then copy the **Site Key** and **Secret Key** into `.env`:

```
RECAPTCHA_SITE_KEY=your-site-key
RECAPTCHA_SECRET_KEY=your-secret-key
```

The site key is used client-side (visible in the page HTML, that's normal),
the secret key is used server-side in `verify_recaptcha()` in `app.py`, which
calls Google's `siteverify` endpoint before the enquiry is accepted.

> **Dev convenience:** if `RECAPTCHA_SECRET_KEY` is left blank, the app logs a
> warning and lets submissions through unverified, so you can test the rest of
> the flow (DB + email) before you've created your Google keys. Don't ship
> to production without setting real keys.

**Form submission flow:**
1. User fills the Enquiry form and answers the captcha.
2. Flask validates fields + captcha.
3. On success: row inserted into `enquiries` table → email sent via SMTP to
   `ADMIN_EMAIL` → success message shown, `email_sent` flag updated in the DB.
4. On failure: form re-renders with specific error messages and a fresh captcha.

**Gallery/Services dynamic data:** both are pulled from Postgres on every
request, so you can add/edit/remove entries by editing the `services` and
`gallery` tables directly — no code changes needed for content updates.

**Images:** gallery/service images currently pull from LoremFlickr
(`loremflickr.com/WIDTHxHEIGHT/tags`), which serves real, freely-usable stock
photos matched to keyword tags — this is why they're realistic industrial/boiler
photos rather than placeholders. Swap any `image_url` in the DB (or seed data
in `schema.sql`) for your own hosted photos whenever you have real site photography —
just replace the URL, everything else keeps working.

## 7. Editing the service catalogue or gallery later

```sql
-- Add a new gallery photo
INSERT INTO gallery (title, category, image_url, display_order)
VALUES ('New Site Install', 'Installations', 'https://yourcdn.com/photo.jpg', 9);

-- Edit a service description
UPDATE services SET full_desc = 'Updated text...' WHERE slug = 'steam-boilers';
```

## 8. Before going live (checklist)

- [ ] Replace placeholder phone/address/email in `templates/base.html` and `contact.html`
- [ ] Point `ADMIN_EMAIL` at the real company inbox
- [ ] Replace LoremFlickr URLs with your own photographed images
- [ ] Set `app.run(debug=False)` and use a real WSGI server (gunicorn/waitress) in production
- [ ] Put `.env` in `.gitignore` — never commit real credentials
- [ ] Consider adding rate-limiting (e.g. Flask-Limiter) on `/enquiry` POST in addition to the captcha
