# Documentation

This document explains how the main parts of this project work — the architecture, auth system, email flows, booking flow, admin panel, and deployment setup.

---

## Architecture Overview

This project uses Django as the web framework but stores almost all application data in MongoDB via MongoEngine. Django's built-in SQLite database is only used for sessions and the auth system, because Django's auth requires a relational database.

Two databases run in parallel:

| Database | What it stores |
|---|---|
| **SQLite** (`/tmp/velvetsteel.db`) | Django auth users and sessions only |
| **MongoDB** | Everything else — reservations, barbers, services, reviews, profiles, site content |

To keep both in sync, the project has a `MongoUser` document that mirrors the Django `User` table. When a user registers or updates their profile, both the Django `User` and the `MongoUser` document get written. This is the standard workaround for using MongoEngine alongside Django's built-in auth.

---

## Directory Structure

### `accounts/`

Handles registration, login, logout, user profiles, password reset, and account deletion.

- `models.py` — defines:
  - `UserProfile` — phone, city, and base64-encoded profile photo
  - `MongoUser` — mirrors Django's `auth_user` table in MongoDB
  - `EmailVerification` — OTP codes for new account verification
  - `PasswordResetRequest` — OTP codes for password reset flow
  - `AccountDeletionRequest` — OTP codes for account deletion confirmation
- `views.py` — all account views and email helpers; see [Auth Flow](#auth-flow) and [Email Flows](#email-flows) below
- `middleware.py` — `MongoAuthMiddleware` attaches `request.user` from session on each request
- `context_processors.py` — injects `user_profile` and `site_settings` into every template automatically

### `reservations/`

Handles everything booking-related plus the admin panel.

- `models.py` — all MongoDB documents:
  - `Service`, `Barber`, `HaircutStyle` — catalogue items
  - `Reservation` — appointment record with status lifecycle
  - `Testimonial` — customer reviews (require staff approval)
  - `GalleryImage` — homepage gallery photos
  - `HomePage`, `AboutPage`, `ServicesPage`, `SiteSettings`, `PrivacyPage`, `TermsPage` — all editable site content
- `views.py` — public views: book form, my reservations, detail, cancel, slots API, booking confirmation email
- `admin_views.py` — all admin panel views (dashboard, CRUD for barbers/services/styles/gallery, analytics, availability)
- `forms.py` — Django forms used in the admin panel
- `urls.py` — public URL patterns under `/reservations/`
- `admin_urls.py` — admin panel URL patterns under `/admin-panel/`

### `barbershop/`

The Django project config.

- `settings.py` — reads from environment variables via `python-dotenv`; connects MongoEngine to MongoDB on startup; no barbershop-specific info (name, phone, etc.) stored here — that's all in `SiteSettings`
- `urls.py` — root URL config
- `views.py` — renders home, about, services, privacy, and terms pages; pulls shop name/contact info from the `SiteSettings` MongoDB document

### `templates/`

All HTML templates. The base layout is `templates/base/base.html` — it includes the navbar, footer, cookie banner, and confirm modal. All public templates extend it.

Admin templates extend `templates/admin_panel/base_admin.html` which has the sidebar and topbar.

Email templates are standalone HTML files with full inline styles — they do not extend the base layout.

### `static/`

- `css/main.css` — full public-facing stylesheet (covers all components and responsive breakpoints)
- `css/admin.css` — admin panel styles
- `js/main.js` — all frontend JS: navbar toggle, alert auto-dismiss, custom select dropdowns, testimonial slider, upload zones, gallery animations, cookie consent, confirm modal

---

## Auth Flow

### Registration

1. User submits the register form (username, email, password, name, phone)
2. Server generates a 6-digit OTP and saves it in `EmailVerification` with a 15-minute expiry
3. A branded HTML email with the code and the shop logo is sent to the user via Gmail SMTP
4. User enters the code on the verify page (max 10 attempts, then the record is deleted)
5. If correct, a Django `User` is created and a `MongoUser` document is also saved as a backup copy in MongoDB
6. The user is logged in immediately and redirected home

### Login

1. User submits username (or email) and password
2. Django's `authenticate()` is tried first (checks SQLite)
3. If that fails — for example after a cold start wiped SQLite — it falls back to `_restore_user_from_mongo()` which verifies the hashed password against the `MongoUser` collection, re-creates the Django `User` from MongoDB, and authenticates
4. On success, a session cookie is set

### Admin Access

Any user with `is_staff=True` gets access to `/admin-panel/`. The `@admin_required` decorator on every admin view checks `request.user.is_staff`. Non-staff users are redirected home with an error.

---

## Email Flows

All emails are sent using Django's `EmailMultiAlternatives` with a full HTML template and a plain-text fallback. Every email template includes the shop logo, branded colours, and inline styles for email client compatibility.

### Verification Email (registration)

- Triggered by: successful register form submission
- Template: `accounts/email_verify.html`
- Contains: 6-digit OTP, valid 15 minutes
- Security: 10-attempt limit; expired codes are deleted automatically

### Password Reset Email

- URL: `/accounts/password-reset/`
- Flow: enter email → receive 6-digit code → enter code → set new password
- Template: `accounts/email_password_reset.html`
- Security: 10-attempt limit, 15-minute expiry; safe response even if email not found (doesn't confirm registration)

### Booking Confirmation Email

- Triggered by: every successful reservation save
- Template: `reservations/email_booking_confirmation.html`
- Contains: confirmation code, barber name, date, time, service, and total price
- Failure is silent (non-blocking) — the booking still succeeds even if email fails

### Account Deletion Email

- URL: `/accounts/delete-account/`
- Flow: click delete on profile → receive 6-digit code → enter code → account permanently deleted
- Template: `accounts/email_delete_account.html`
- Security: 5-attempt limit, 15-minute expiry; deletes Django User, MongoUser, and UserProfile on confirmation

---

## Booking Flow

### How a Reservation is Created

1. Customer visits `/reservations/book/`
2. They pick a barber, a haircut style, an optional service, a date, and a time
3. When the barber and date are selected, the frontend calls `/reservations/api/slots/?barber_id=X&date=Y` which returns all 30-minute slots from 8:00 AM to 7:30 PM minus any already-booked ones
4. Customer picks a time from the slot grid
5. On form submit, the server re-validates everything: barber exists, haircut style exists, date is today or future, slot isn't already taken (pending or confirmed)
6. A `Reservation` document is saved with a randomly generated 8-character confirmation code
7. A booking confirmation email is automatically sent to the customer
8. Customer is redirected to the reservation detail page

### Reservation Status Lifecycle

| Status | Meaning |
|---|---|
| `pending` | Just booked, awaiting staff confirmation |
| `confirmed` | Staff confirmed the appointment |
| `completed` | Appointment took place |
| `cancelled` | Cancelled by customer or staff |
| `no_show` | Customer didn't show up |

Customers can cancel their own pending/confirmed future reservations. Staff can set any status from the admin panel.

---

## Image Storage

There is no external file storage (no S3, no persistent media folder). All uploaded images — barber photos, service images, gallery images, and profile photos — are converted to base64 data URIs and stored directly in MongoDB as strings.

The `_image_to_data_uri()` helper in `admin_views.py` handles the conversion. This works fine for a low-to-medium traffic site. For high-volume production, switch to an object storage service (S3, Cloudflare R2) and store URLs instead.

---

## Content Management

All editable site content is stored in MongoDB and managed through the admin panel at `/admin-panel/`. Changes take effect immediately on the public site.

| Model | What it controls |
|---|---|
| `SiteSettings` | Shop name, footer contact info, social links |
| `HomePage` | Hero text, feature descriptions, location section, map embed |
| `AboutPage` | Story text, stats, shop photo, values list, contact info |
| `ServicesPage` | Hero subtitle and section text |
| `PrivacyPage` | All privacy policy sections |
| `TermsPage` | All terms of service sections |

The views pull shop name, phone, address, and email directly from `SiteSettings` — there are no environment variables for this. If no `SiteSettings` document exists yet, defaults from the model are used until the admin saves settings.

---

## Admin Panel

The admin panel lives at `/admin-panel/` and is completely separate from Django's built-in `/django-admin/`. Every view uses the `@admin_required` decorator.

### Dashboard
Today's booking count, pending/confirmed counts, today's revenue, and monthly revenue. The 10 most recent reservations with inline status-update dropdowns.

### Reservations
Full list with filters (status, date, barber), inline status updates, and bulk delete.

### Live Availability
All active barbers' slot grids for any selected date, auto-refreshing every 60 seconds. Uses the same slot API the booking form uses.

### Analytics
Bar chart (bookings per day) and line chart (revenue per day) for the last 7 days using Chart.js. Top services by booking count and all barbers sorted by bookings.

### Content Editing
Separate edit pages for Home, About, Services, Privacy Policy, and Terms of Service. All changes go live immediately.

---

## Security Practices

- No barbershop contact info stored in environment variables — all managed in the database
- No console logging of connection info or sensitive data in production
- Passwords hashed by Django's auth system (PBKDF2)
- CSRF protection on all forms
- Email OTP codes: rate-limited, short-lived (15 minutes), deleted after use or too many attempts
- Account deletion requires a separate email confirmation — not just a button click
- Password reset uses the same code pattern; does not reveal whether an email is registered
- `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SECURE = True` in production (when `DEBUG=False`)
- WhiteNoise serves static files securely with compression

---

## Management Commands

| Command | What it does |
|---|---|
| `python manage.py seed_data` | Creates sample barbers, services, haircut styles, testimonials, and an admin user |
| `python manage.py sync_users` | Syncs all `MongoUser` records to Django's SQLite `auth_user` table — run this if users can't log in after a database reset |

---

## Deployment

Other Platforms (Render, Railway, Fly.io)

Use the `Procfile`:
```
web: gunicorn barbershop.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

Or use `start.sh` which handles the pre-start steps automatically. Set all required environment variables in the platform dashboard.

### Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Long random Django secret key — never commit this |
| `DEBUG` | Yes | `False` in production |
| `MONGODB_URI` | Yes | Full MongoDB Atlas connection string |
| `EMAIL_BACKEND` | Yes | `django.core.mail.backends.smtp.EmailBackend` for real email sending |
| `EMAIL_HOST_USER` | Yes | Gmail address used as sender |
| `EMAIL_HOST_PASSWORD` | Yes | Gmail App Password (16 characters from myaccount.google.com/apppasswords) |
| `ALLOWED_HOSTS` | No | Comma-separated extra hostnames |
| `CSRF_TRUSTED_ORIGINS` | No | Comma-separated extra HTTPS origins |
