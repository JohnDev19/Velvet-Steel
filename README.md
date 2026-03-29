# Velvet Steel Barbershop — Full Stack Reservation System

A fully responsive barbershop reservation system built with Django and MongoDB.

---

## Features

### Customer-Facing
- Landing page with hero, services, barbers, testimonials, and location
- Full services page with pricing (P500 to P1,800)
- About page with team bios and contact details
- Online booking with real-time slot availability per barber and date
- My Reservations — view, manage, and cancel bookings
- User accounts — register, login, edit profile

### Admin Panel (/admin-panel/)
- Dashboard with live stats: today's bookings, revenue, status breakdown
- Reservations management with status filtering and inline status updates
- Analytics with 7-day booking and revenue charts
- Service and barber management (via Django admin integration)
- Review moderation — approve or reject testimonials

### Technical
- Django 4.2 with MongoDB via Djongo
- Fully responsive — mobile, tablet, desktop
- Custom CSS
- WhiteNoise static file serving for production

---

## Setup

### Requirements

- Python 3.10 or higher
- MongoDB 6.0 or higher (local or Atlas)
- pip

### 1. Create a virtual environment

    python -m venv venv
    source venv/bin/activate        # macOS / Linux
    venv\Scripts\activate           # Windows

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Configure environment

    cp .env.example .env

Edit .env and set at minimum:

    SECRET_KEY=your-generated-secret-key
    DEBUG=True
    MONGODB_URI=mongodb://localhost:27017
    MONGODB_DB=barbershop_db

Generate a secret key:

    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

### 4. Start MongoDB

Local:

    mongod --dbpath /your/data/path

Or set MONGODB_URI to a MongoDB Atlas connection string.

### 5. Run migrations

    python manage.py makemigrations
    python manage.py migrate

### 6. Seed sample data

    python manage.py seed_data

Creates: 10 services, 4 barbers, 5 testimonials, admin account, and a test customer.

### 7. Start the server

    python manage.py runserver

Open: http://127.0.0.1:8000

---

## Default Credentials

After running seed_data:

    Admin      username: admin     password: admin123
    Customer   username: juandc    password: password123

Change these immediately before any production use.

---

## URL Reference

    /                            Homepage
    /about/                      About and team
    /services/                   Full service menu
    /reservations/book/          Book appointment
    /reservations/my/            My reservations
    /accounts/login/             Login
    /accounts/register/          Register
    /accounts/profile/           Edit profile
    /admin-panel/                Admin dashboard
    /admin-panel/reservations/   Manage all bookings
    /admin-panel/analytics/      Charts and performance
    /admin-panel/services/       Service listings
    /admin-panel/barbers/        Barber profiles
    /admin-panel/testimonials/   Review moderation
    /django-admin/               Django built-in admin

---

## Project Structure

    barbershop/
    +-- barbershop/
    |   +-- settings.py          Settings (reads from .env)
    |   +-- urls.py              Root URL config
    |   +-- views.py             Home, About, Services views
    +-- reservations/
    |   +-- models.py            Service, Barber, Reservation, Testimonial
    |   +-- views.py             Customer booking views
    |   +-- admin_views.py       Admin panel views
    |   +-- forms.py             Booking and testimonial forms
    |   +-- management/
    |       +-- commands/
    |           +-- seed_data.py Sample data seeder
    +-- accounts/
    |   +-- models.py            UserProfile
    |   +-- views.py             Login, register, profile
    +-- templates/
    |   +-- base/base.html       Main site layout
    |   +-- home/                Homepage and services page
    |   +-- about/               About page
    |   +-- reservations/        Booking, my bookings, detail
    |   +-- accounts/            Login, register, profile
    |   +-- admin_panel/         Full admin dashboard
    +-- static/
    |   +-- css/main.css         Site CSS
    |   +-- css/admin.css        Admin panel CSS
    |   +-- js/main.js           Navbar, animations, booking logic
    +-- .env.example
    +-- requirements.txt
    +-- manage.py
    +-- Procfile

---

## Service Pricing

    Signature Haircut              P600    45 min
    Precision Fade                 P750    60 min
    Textured Crop                  P700    50 min
    Classic Straight Razor Shave   P650    45 min
    Beard Sculpture                P500    30 min
    Scalp and Hair Treatment       P800    60 min
    Fade and Wash                  P850    60 min
    Gentleman Package              P1,200  90 min
    Velvet Steel Complete          P1,800  120 min
    Youth Cut                      P500    30 min

---

## Production Deployment

Set in .env:

    DEBUG=False
    SECRET_KEY=a-very-strong-unique-secret-key
    ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
    MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/

With Gunicorn:

    gunicorn barbershop.wsgi:application --bind 0.0.0.0:8000 --workers 3

For Railway, Render, or Heroku — set env vars in the dashboard and use the included Procfile.

---

## Stack

    Django 4.2       Web framework
    Djongo 1.3.6     Django to MongoDB ORM adapter
    PyMongo 3.12     MongoDB Python driver
    Pillow 10.3      Image upload handling
    WhiteNoise 6.7   Static file serving
    Gunicorn 22.0    WSGI production server
    python-dotenv    Environment variable loading
    Chart.js (CDN)   Analytics charts in admin panel
    Font Awesome 6   Icons
    Google Fonts     Playfair Display, Josefin Sans, Cormorant Garamond

---
