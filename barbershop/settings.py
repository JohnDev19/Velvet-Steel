import os
import mongoengine
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ── CORE ─────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',
    'velvet-steel-ph.vercel.app',
] + [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://velvet-steel-ph.vercel.app',
] + [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

# ── APPS ─────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservations',
    'accounts',
]

# ── MIDDLEWARE ───────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'accounts.middleware.MongoAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'barbershop.urls'

# ── TEMPLATES ────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'barbershop.wsgi.application'

# ── DATABASE ─────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}

# ── MONGODB via MongoEngine ──────────────────────────────────
MONGODB_URI = os.environ.get('MONGODB_URI', '')

if MONGODB_URI:
    mongoengine.connect(host=MONGODB_URI, alias='default')
else:
    import sys
    print("WARNING: MONGODB_URI not set", file=sys.stderr)

# ── SESSIONS ─────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = not DEBUG

# ── MESSAGES ─────────────────
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

# ── INTERNATIONALISATION ─────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

# ── STATIC & MEDIA ───────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── AUTH REDIRECTS ───────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ── EMAIL ────────────────────────────────────────────────────
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@velvetsteel.ph')

# ── BARBERSHOP INFO ──────────────────────────────────────────
BARBERSHOP_NAME = os.environ.get('BARBERSHOP_NAME', 'Velvet Steel Barbershop')
BARBERSHOP_PHONE = os.environ.get('BARBERSHOP_PHONE', '+63 912 345 6789')
BARBERSHOP_ADDRESS = os.environ.get('BARBERSHOP_ADDRESS', '123 Rizal Avenue, Quezon City, Metro Manila')
BARBERSHOP_EMAIL = os.environ.get('BARBERSHOP_EMAIL', 'info@velvetsteel.ph')