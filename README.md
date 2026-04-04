# Velvet Steel Barbershop

A full-stack barbershop booking web app built with Django and MongoDB. Customers book appointments, pick a barber, choose a haircut style, manage their reservations, and leave reviews. Staff manage everything through dashboard.

Good starting point for people learning Django + MongoDB, or students wanting a full-stack web app example to study or build on.

---

## Features

**Customer**
- Register with email OTP verification (6-digit code, 15-minute expiry)
- Book appointments — pick barber, service, haircut style, date, and time
- Slot availability (no double-booking)
- View, track, and cancel reservations
- Write reviews for completed appointments
- Upload profile photo
- Personal dashboard with booking history and spending stats

**Admin panel** (`/admin-panel/`)
- Dashboard with today's bookings, pending count, and revenue
- Reservations list with status updates, filters, and bulk delete
- Manage barbers, services, haircut styles — all with image uploads
- Live availability view showing every barber's slots for any date
- Approve or reject customer reviews
- Analytics charts — bookings and revenue for the last 7 days
- Edit all public page content (home, about, services, privacy policy, terms)
- Site settings — shop name, footer info, social links
- Gallery management (8-image mosaic displayed on homepage)

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
| Deployment | Vercel (serverless) or any Linux host |
| Frontend | HTML, CSS, Vanilla JS (no framework) |

---

## Project Structure

```
velvet-steel-barbershop/
├── accounts/               # Auth, user profiles, email verification
│   ├── models.py           # UserProfile, MongoUser, EmailVerification
│   ├── views.py            # Register, login, logout, dashboard, profile
│   ├── urls.py
│   └── middleware.py       # MongoAuthMiddleware
├── reservations/           # Core booking system + admin panel
│   ├── models.py           # Reservation, Service, Barber, Testimonial, etc.
│   ├── views.py            # Public booking views
│   ├── admin_views.py      # All admin panel views
│   ├── admin_urls.py       # Admin panel URL routes
│   ├── urls.py             # Public reservation URL routes
│   └── forms.py            # Django forms for admin
├── barbershop/             # Django project config
│   ├── settings.py
│   ├── urls.py             # Root URL config
│   └── views.py            # Home, about, services pages
├── templates/              # All HTML templates
│   ├── base/base.html      # Base layout with nav and footer
│   ├── home/               # Public pages
│   ├── reservations/       # Booking, my reservations, detail pages
│   ├── accounts/           # Login, register, dashboard, profile
│   └── admin_panel/        # All admin panel pages
├── static/
│   ├── css/main.css        # Main stylesheet
│   ├── css/admin.css       # Admin panel styles
│   └── js/main.js          # Main JS (nav, custom selects, sliders)
├── api/index.py            # Vercel serverless entry point
├── manage.py
└── requirements.txt
```

---

## Setup

### Requirements

- Python 3.12
- MongoDB (local install or MongoDB Atlas free tier)
- Gmail account with an App Password set up

### Steps

**1. Clone**
```bash
git clone <your-repo-url>
cd velvet-steel-barbershop
```

**2. Virtual environment**
```bash
python -m venv venv
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

**3. Install packages**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Edit .env with your values
```

**5. Run migrations**
```bash
python manage.py migrate --run-syncdb
```

**6. Seed sample data** (barbers, services, haircut styles, admin user)
```bash
python manage.py seed_data
```
The admin password prints to the console once. Save it.

**7. Start dev server**
```bash
python manage.py runserver
```

- Site: http://localhost:8000
- Admin panel: http://localhost:8000/admin-panel/
- Django admin: http://localhost:8000/django-admin/

---

## Default Credentials

After `seed_data`, the admin account is:
- **Username**: `admin`
- **Password**: printed once to the console when seed runs

To set a custom password before seeding, add this to `.env`:
```
ADMIN_SEED_PASSWORD=your-password-here
```

---

## Deployment

The project includes a `Procfile` for platforms like Render and Railway, and a `vercel.json` for Vercel.

For any deployment, you need:
- `SECRET_KEY` set to a long random string
- `DEBUG=False`
- `MONGODB_URI` pointing to your Atlas cluster
- `ALLOWED_HOSTS` including your domain
- Email SMTP variables filled in

---

## License

MIT — use it, modify it, learn from it.