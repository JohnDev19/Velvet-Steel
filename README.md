# Velvet Steel Barbershop

A full-stack barbershop booking web app built with Django and MongoDB. Customers book appointments, pick a barber, choose a haircut style, manage their reservations, and leave reviews. Staff manage everything through dashboard.

Good starting point for people learning Django + MongoDB, or students wanting a full-stack web app example to study or build on.

---

![](1.jpg)
![](2.jpg)
![](3.jpg)
![](4.jpg)
![](5.jpg)
![](6.jpg)
![](7.jpg)
![](8.jpg)
![](9.jpg)

---

## Features

### Customer
- Register with email OTP verification (6-digit code, 15-minute expiry, brute-force protected)
- **Password reset** via email code (3-step: request → verify code → set new password)
- **Booking confirmation emails** sent automatically on every reservation
- **Account deletion** with email confirmation code required
- Book appointments — pick barber, haircut style, optional service, date, and time slot
- Real-time slot availability (no double-booking per barber)
- View, track, and cancel reservations
- Write reviews for completed appointments
- Upload profile photo
- Personal dashboard with booking history and spending stats

### Admin Panel (`/admin-panel/`)
- Dashboard with today's bookings, pending count, and daily/monthly revenue
- Reservations list with status updates, filters, and bulk delete
- Manage barbers, services, and haircut styles — all with image uploads
- Live availability view showing every barber's slots for any date
- Approve or reject customer reviews
- Analytics charts — bookings and revenue for the last 7 days
- Edit all public page content (home, about, services, privacy policy, terms)
- Site settings — shop name, footer info, social links
- Gallery management (8-image mosaic on homepage)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | Django 4.2 |
| Database | MongoDB via MongoEngine |
| Python | 3.12 |
| Auth | Django auth + custom MongoDB sync layer |
| Email | Gmail SMTP with App Password |
| Static files | WhiteNoise |
| WSGI server | Gunicorn |
| Deployment | Vercel Render, Railway, or any Linux host |
| Frontend | HTML, CSS, Vanilla JS (no framework) |

---

## Project Structure

```
velvet-steel-barbershop/
├── accounts/                     # Auth, user profiles, email flows
│   ├── models.py                 # UserProfile, MongoUser, EmailVerification,
│   │                             #   PasswordResetRequest, AccountDeletionRequest
│   ├── views.py                  # Register, login, logout, dashboard, profile,
│   │                             #   password reset, account deletion
│   ├── urls.py
│   ├── middleware.py             # MongoAuthMiddleware
│   └── context_processors.py    # Injects user_profile + site_settings into templates
├── reservations/                 # Core booking system + admin panel
│   ├── models.py                 # Reservation, Service, Barber, Testimonial,
│   │                             #   HaircutStyle, GalleryImage, HomePage,
│   │                             #   AboutPage, ServicesPage, SiteSettings,
│   │                             #   PrivacyPage, TermsPage
│   ├── views.py                  # Public booking views + booking confirmation email
│   ├── admin_views.py            # All admin panel views
│   ├── admin_urls.py             # Admin panel URL routes
│   ├── urls.py                   # Public reservation URL routes
│   └── forms.py                  # Django forms for admin
├── barbershop/                   # Django project config
│   ├── settings.py
│   ├── urls.py                   # Root URL config
│   └── views.py                  # Home, about, services pages
├── templates/
│   ├── base/base.html            # Base layout — nav, footer, cookie banner
│   ├── home/                     # Public pages (home, services, privacy, terms)
│   ├── reservations/             # Book, my reservations, detail, review
│   │   └── email_booking_confirmation.html
│   ├── accounts/                 # Login, register, verify, dashboard, profile,
│   │   │                         #   password reset, account deletion
│   │   ├── email_verify.html
│   │   ├── email_password_reset.html
│   │   └── email_delete_account.html
│   └── admin_panel/              # All admin panel pages
├── static/
│   ├── css/main.css              # Full public stylesheet
│   ├── css/admin.css             # Admin panel styles
│   └── js/main.js                # Nav, alerts, dropdowns, sliders, gallery
├── start.sh                      # Startup script (migrate → sync → static → gunicorn)
├── manage.py
└── requirements.txt
```

---

## Setup

### Requirements

- Python 3.12
- MongoDB (local install or MongoDB Atlas free tier)
- Gmail account with an App Password

### Local Setup

**1. Clone**
```bash
git clone <your-repo-url>
cd velvet-steel-barbershop
```

**2. Install packages**
```bash
pip install -r requirements.txt
```

**3. Configure environment**
```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables below)
```

**4. Run migrations**
```bash
python manage.py migrate --run-syncdb
```

**5. Seed sample data** (barbers, services, haircut styles, admin user)
```bash
python manage.py seed_data
```
The admin password prints once to the console. Save it.

**6. Start dev server**
```bash
python manage.py runserver 0.0.0.0:5000
```

- Site: http://localhost:5000
- Admin panel: http://localhost:5000/admin-panel/
- Django admin: http://localhost:5000/django-admin/

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Long random Django secret key |
| `DEBUG` | Yes | `True` for development, `False` for production |
| `MONGODB_URI` | Yes | MongoDB Atlas connection string (`mongodb+srv://...`) |
| `EMAIL_BACKEND` | Yes | `django.core.mail.backends.smtp.EmailBackend` for production |
| `EMAIL_HOST_USER` | Yes | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Yes | Gmail App Password (not your account password) |
| `ALLOWED_HOSTS` | No | Comma-separated extra hostnames (vercel domains auto-detected) |
| `CSRF_TRUSTED_ORIGINS` | No | Extra HTTPS origins for CSRF |

> Barbershop name, phone, address, and email are managed through the admin panel under **Site Settings** — no environment variables needed.

### Generating a Gmail App Password

1. Enable 2-Step Verification on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password for "Mail"
4. Use that 16-character password as `EMAIL_HOST_PASSWORD`

---

## Deployment on Vercel

The app is configured to run on Vercel out of the box.

- Port 5000, served by Gunicorn via `start.sh`
- Vercel domain (`.vercel.app`,) is automatically allowed
- Set `SECRET_KEY`, `MONGODB_URI`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `EMAIL_BACKEND` in the Vercel Environment Variables tab.

---

## Default Admin Account

After running `seed_data`, the admin account is:
- **Username**: `admin`
- **Password**: printed to console on first run

To set a custom password before seeding:
```
ADMIN_SEED_PASSWORD=your-password-here
```

---

## Management Commands

| Command | What it does |
|---|---|
| `python manage.py seed_data` | Seeds sample data and creates admin user |
| `python manage.py sync_users` | Syncs MongoUser records to Django's SQLite auth table |

---

## License

MIT — use it, modify it, learn from it.
