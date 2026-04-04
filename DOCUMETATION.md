# Documentation

This document explains how the main parts of this project work. It covers the architecture, the auth system, booking flow, admin panel, and deployment setup.

---

## Architecture Overview

This project uses Django as the web framework but stores almost all data in MongoDB via MongoEngine. Django's built-in SQLite database is only used for sessions and the auth system (because Django's auth requires a relational database).

This means there are effectively two databases running in parallel:
- **SQLite** (`/tmp/velvetsteel.db`) — stores Django's auth users and sessions
- **MongoDB** — stores everything else: reservations, barbers, services, reviews, profiles, site content

To keep both in sync, the project has a `MongoUser` document that mirrors the Django `User` table. When a user registers or updates their profile, both the Django User and the MongoUser document get written.

This is a known workaround when you want to use MongoEngine with Django's built-in auth. It adds some complexity but makes the auth system work correctly.

---

## Directory Structure Explained

### `accounts/`

Handles registration, login, logout, user profiles, and email verification.

- `models.py` — defines `UserProfile` (phone, city, photo), `MongoUser` (mirrors Django User), and `EmailVerification` (OTP codes)
- `views.py` — registration creates an `EmailVerification` record and sends the OTP via email; on verification it creates both the Django `User` and `MongoUser`; login tries Django auth first, then falls back to the MongoDB copy
- `middleware.py` — `MongoAuthMiddleware` attaches `request.user` from the session on each request
- `context_processors.py` — injects `user_profile` and `site_settings` into every template automatically

### `reservations/`

Handles everything booking-related plus the admin panel.

- `models.py` — all the MongoDB documents: `Service`, `Barber`, `Reservation`, `Testimonial`, `HaircutStyle`, `GalleryImage`, plus content documents (`HomePage`, `AboutPage`, `ServicesPage`, `SiteSettings`, `PrivacyPage`, `TermsPage`)
- `views.py` — public views: book form, my reservations, detail page, cancel, testimonial submit, available slots API
- `admin_views.py` — all admin panel views (dashboard, CRUD for barbers/services/styles/gallery, analytics, availability)
- `forms.py` — Django forms used in the admin panel for creating/editing records
- `urls.py` — public URL patterns under `/reservations/`
- `admin_urls.py` — admin panel URL patterns under `/admin-panel/`

### `barbershop/`

The Django project config.

- `settings.py` — all Django settings; reads from `.env` via `python-dotenv`; connects MongoEngine to MongoDB at startup
- `urls.py` — root URL config; includes accounts, reservations, and admin panel URL sets
- `views.py` — renders the home, about, services, privacy, and terms pages

### `templates/`

Standard Django templates. The base layout is `templates/base/base.html` — it includes the navbar, footer, cookie banner, and confirm modal. All other templates extend it.

Admin templates all extend `templates/admin_panel/base_admin.html` which has the sidebar and topbar.

### `static/`

- `css/main.css` — the entire public-facing stylesheet (8000+ lines; covers all components and responsive breakpoints)
- `css/admin.css` — admin panel specific styles
- `js/main.js` — all frontend JS: navbar toggle, alerts auto-dismiss, custom select dropdowns, testimonial slider, upload zones, gallery animations, cookie consent, confirm modal

### `api/index.py`

Kapag sa Vercel mo ide-deploy, well, look at the Vercel serverless entry point. On cold start, it runs migrations, syncs MongoDB users to SQLite, collects static files, and creates the admin user if one doesn't exist. This is needed because Vercel's filesystem resets between deploys.

---

## Auth Flow

### Registration

1. User fills out the register form (username, email, password, name, phone)
2. The server generates a 6-digit code and saves it in `EmailVerification` with a 15-minute expiry
3. The code is emailed to the user via Gmail SMTP
4. User enters the code on the verify page
5. If correct, a Django `User` is created and a `MongoUser` document is also saved as a backup copy
6. The user is logged in immediately

### Login

1. User submits username + password
2. Django's `authenticate()` is tried first (checks the SQLite User table)
3. If that fails (happens on Vercel cold starts where SQLite was wiped), it falls back to `_restore_user_from_mongo()` which checks the `MongoUser` collection, verifies the hashed password, re-creates the Django User from MongoDB, and authenticates
4. On success, a session cookie is set

This two-step login fallback is why users don't get locked out after Vercel resets the SQLite database.

### Admin Access

Any user with `is_staff=True` on their Django User gets access to `/admin-panel/`. The `admin_required` decorator on admin views checks `request.user.is_staff`. Regular users see a 403 redirect.

---

## Booking Flow

### How a Reservation is Created

1. Customer visits `/reservations/book/`
2. They pick a barber (from active Barbers), an optional service, a haircut style, a date, and a time
3. When the barber and date are selected, the frontend calls `/reservations/api/slots/?barber_id=X&date=Y` — this returns the list of times that don't have a pending/confirmed reservation already
4. Customer picks a time from the slot grid
5. On form submit, the server re-validates everything: checks the barber exists, haircut style exists, date is in the future, and the slot isn't already taken
6. A `Reservation` document is created with a randomly generated 8-character confirmation code
7. The customer is redirected to the reservation detail page

### Reservation Statuses

| Status | Meaning |
|---|---|
| `pending` | Just booked, not yet confirmed by staff |
| `confirmed` | Staff confirmed it |
| `completed` | Appointment happened |
| `cancelled` | Cancelled by customer or staff |
| `no_show` | Customer didn't show up |

Customers can cancel their own pending/confirmed reservations. Staff can set any status from the admin panel.

### Slot Availability

The `get_available_slots` view generates all 30-minute slots from 8:00 AM to 7:30 PM, then removes any that have a pending or confirmed reservation for that barber on that date. The remaining slots are returned as JSON.

---

## Image Storage

There is no file storage service (no S3, no media folder that persists). All uploaded images — barber photos, service images, gallery images, profile photos — are converted to base64 data URIs and stored directly in MongoDB as strings.

This works fine for a demo or low-traffic site. For production with many uploads, you'd want to switch to an object storage service like S3 or Cloudflare R2 and store URLs instead.

The `_image_to_data_uri()` helper in `admin_views.py` handles the conversion.

---

## Content Management

The following MongoDB documents store editable site content:

| Model | What it controls |
|---|---|
| `HomePage` | Hero text, feature descriptions, section subtitles, location info, map embed |
| `AboutPage` | About page text, stats, shop photo, values, contact info |
| `ServicesPage` | Services page hero text and subtitle |
| `SiteSettings` | Shop name, footer content, social links |
| `PrivacyPage` | All sections of the privacy policy |
| `TermsPage` | All sections of the terms of service |

All of these are edited through the admin panel and take effect immediately on the public site. The templates check for the document and fall back to default text if it doesn't exist yet.

---

## Admin Panel

The admin panel lives under `/admin-panel/` and is separate from Django's built-in `/django-admin/`.

Every admin view uses the `@admin_required` decorator which redirects to login if the user isn't authenticated and redirects home with an error if they're not staff.

### Dashboard

Shows today's booking count, pending/confirmed counts, today's revenue, and monthly revenue. Lists the 10 most recent reservations with inline status update dropdowns.

### Live Availability

Fetches slot data for all active barbers for a given date using the same `get_available_slots` API the booking form uses. Auto-refreshes every 60 seconds. Hovering a booked slot shows a tooltip (currently just "Booked" — would need extra data to show customer name).

### Analytics

Shows a bar chart (bookings per day) and line chart (revenue per day) for the last 7 days using Chart.js. Also shows the top 5 services by booking count and all barbers sorted by booking count.

---

## Email

Email is sent using Django's `EmailMultiAlternatives` with an HTML template (`accounts/email_verify.html`). The template is a standalone HTML email with inline styles.

In development with `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`, emails print to the terminal instead of being sent.

For Gmail SMTP in production, you need to generate an App Password at https://myaccount.google.com/apppasswords. Do not use your regular Gmail password.

---

## Management Commands

| Command | What it does |
|---|---|
| `python manage.py seed_data` | Creates sample barbers, services, haircut styles, testimonials, and admin user |
| `python manage.py sync_users` | Syncs `MongoUser` records to the Django SQLite `auth_user` table |
| `python manage.py migrate_haircut_categories` | One-time migration to update old haircut category values to the new price-tier system |

---

## Deployment

### Vercel

The `vercel.json` routes all requests to `api/index.py`. The `api/index.py` file runs setup on cold start (migrations, user sync, static files) then returns a WSGI app. Environment variables are set in the Vercel project dashboard.

Note: Vercel's SQLite is ephemeral. That's why the `sync_users` logic exists — to restore Django users from MongoDB on every cold start.

### Other Platforms (Render, Railway, Fly.io)

Use the `Procfile`:
```
web: gunicorn barbershop.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

Or use `start.sh` which runs migrations and sync before starting gunicorn.

The `SECRET_KEY`, `MONGODB_URI`, and email variables must all be set as environment variables on whatever platform you use.

---

## Environment Variables Reference

See `.env.example` for the full list with descriptions.

Key ones:
- `SECRET_KEY` — long random string, never commit this
- `DEBUG` — set to `False` in production
- `MONGODB_URI` — your MongoDB connection string
- `EMAIL_BACKEND` — set to SMTP backend in production
- `EMAIL_HOST_PASSWORD` — must be a Gmail App Password, not your account password
- `ALLOWED_HOSTS` — your domain name(s), comma-separated

---

## Known Limitations

- Images are stored as base64 in MongoDB — works fine for demos, not ideal for large-scale production
- No password reset flow (not implemented)
- No email notifications for booking confirmations (not implemented)
- SQLite is ephemeral on Vercel — the sync_users system compensates but adds cold start time
- No pagination on reservations or reviews lists

I'm gonna implement them.