-- =========================================================
--  Ignis Boiler Works — Database Schema
--  Run with: psql -U postgres -d boiler_db -f schema.sql
-- =========================================================

DROP TABLE IF EXISTS enquiries CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS gallery CASCADE;

-- 1) ENQUIRY FORM SUBMISSIONS ------------------------------
CREATE TABLE enquiries (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(120)  NOT NULL,
    email         VARCHAR(150)  NOT NULL,
    phone         VARCHAR(20)   NOT NULL,
    service       VARCHAR(120),
    message       TEXT          NOT NULL,
    submitted_at  TIMESTAMP     NOT NULL DEFAULT NOW(),
    email_sent    BOOLEAN       NOT NULL DEFAULT FALSE
);

-- 2) SERVICES / CLIENT-FACING CATALOGUE DATA ---------------
CREATE TABLE services (
    id            SERIAL PRIMARY KEY,
    slug          VARCHAR(80)   UNIQUE NOT NULL,
    title         VARCHAR(120)  NOT NULL,
    tagline       VARCHAR(200),
    short_desc    TEXT,
    full_desc     TEXT,
    image_url     TEXT,
    icon          VARCHAR(10),
    display_order INT DEFAULT 0
);

-- 3) GALLERY (dynamic image entries) -----------------------
CREATE TABLE gallery (
    id            SERIAL PRIMARY KEY,
    title         VARCHAR(150),
    category      VARCHAR(80),
    image_url     TEXT NOT NULL,
    display_order INT DEFAULT 0
);

-- ---------------------------------------------------------
-- SEED DATA
-- ---------------------------------------------------------

INSERT INTO services (slug, title, tagline, short_desc, full_desc, image_url, icon, display_order) VALUES
(
  'steam-boilers',
  'Industrial Steam Boilers',
  'High-pressure steam, engineered for continuous duty.',
  'Fire-tube and water-tube steam boilers built for textile, food processing, and chemical plants that cannot afford downtime.',
  'Our industrial steam boilers are designed for facilities that run around the clock. Each unit is built to ASME-equivalent pressure vessel standards, with a fully automated combustion control system that keeps efficiency above 85% even under variable load. We size every boiler around your steam demand curve rather than selling off-the-shelf capacity, which means lower fuel bills over the unit''s working life. Typical applications include textile dyeing units, food and beverage sterilization, rubber curing, and chemical process heating. Every installation includes a commissioning report, safety valve certification, and a 24-month workmanship warranty. Our service team also offers scheduled descaling and tube-inspection visits so pressure vessels stay within statutory inspection compliance.',
  'https://loremflickr.com/900/650/steam,boiler,industrial?lock=101',
  '⚙',
  1
),
(
  'hot-water-heating',
  'Hot Water & Heating Systems',
  'Consistent thermal comfort for commercial and institutional buildings.',
  'Hot water generators and centralised heating systems for hospitals, hotels, and large residential campuses.',
  'For buildings where hot water is a daily operational necessity — hospitals, hotels, hostels, and manufacturing units needing process hot water — we design centralised hot water generation systems that replace dozens of inefficient point heaters with one monitored, serviceable plant room. Systems are available in oil, gas, and hybrid electric configurations, sized against your peak simultaneous demand rather than average use, which is the single most common design mistake in this category. Insulated distribution loops and recirculation pumps are included in every proposal so heat isn''t lost between the plant room and the tap. We also retrofit existing boiler rooms, replacing ageing calorifiers without needing to re-plan the whole plant room layout.',
  'https://loremflickr.com/900/650/pipes,heating,industrial?lock=102',
  '🔥',
  2
),
(
  'amc-maintenance',
  'AMC & Preventive Maintenance',
  'Because a boiler failure is never a convenient time.',
  'Annual maintenance contracts covering inspection, descaling, safety valve testing, and emergency breakdown response.',
  'A boiler that isn''t maintained on schedule doesn''t fail gracefully — it fails during your busiest production week. Our Annual Maintenance Contracts are built around statutory inspection intervals and include quarterly combustion tuning, annual descaling, safety valve and pressure gauge calibration, refractory inspection, and water-treatment audits to control scale and corrosion. AMC clients also get priority breakdown response, with our engineers targeting on-site arrival within a committed response window rather than a best-effort callback. Every visit closes with a written condition report, so plant managers have a documented maintenance trail for insurance and statutory audits, not just a technician''s word that "it''s fine."',
  'https://loremflickr.com/900/650/engineer,maintenance,factory?lock=103',
  '🛠',
  3
);

INSERT INTO gallery (title, category, image_url, display_order) VALUES
('Boiler House Floor',        'Installations', 'https://loremflickr.com/700/500/boiler,room?lock=201', 1),
('Steam Distribution Header', 'Installations', 'https://loremflickr.com/700/500/steam,pipes?lock=202', 2),
('Site Commissioning',        'Field Work',     'https://loremflickr.com/700/500/engineer,factory?lock=203', 3),
('Pressure Gauge Detail',     'Components',     'https://loremflickr.com/700/500/gauge,industrial?lock=204', 4),
('Fabrication Yard',          'Manufacturing',  'https://loremflickr.com/700/500/steel,fabrication?lock=205', 5),
('Insulated Pipe Runs',       'Installations',  'https://loremflickr.com/700/500/pipes,insulation?lock=206', 6),
('Control Panel Upgrade',     'Field Work',      'https://loremflickr.com/700/500/control,panel,industrial?lock=207', 7),
('Annual Inspection Visit',   'Maintenance',    'https://loremflickr.com/700/500/technician,boiler?lock=208', 8);
