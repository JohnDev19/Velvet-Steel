import os
import random
import string
import base64
from datetime import datetime, timedelta

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django import forms
from .models import UserProfile, EmailVerification


# ── helpers ─────────────────────────────────────────────────────────────────

def _get_or_create_profile(user):
    try:
        profile = UserProfile.objects(user_id=user.pk).first()
        if not profile:
            profile = UserProfile(user_id=user.pk)
            profile.save()
        return profile
    except Exception:
        return UserProfile(user_id=user.pk)


def _persist_user_to_mongo(dj_user):
    try:
        from .models import MongoUser
        mu = MongoUser.objects(username=dj_user.username).first()
        if mu is None:
            mu = MongoUser(username=dj_user.username)
        mu.django_id    = dj_user.pk
        mu.email        = dj_user.email
        mu.first_name   = dj_user.first_name
        mu.last_name    = dj_user.last_name
        mu.password     = dj_user.password   # already hashed
        mu.is_active    = dj_user.is_active
        mu.is_staff     = dj_user.is_staff
        mu.is_superuser = dj_user.is_superuser
        mu.date_joined  = dj_user.date_joined
        mu.save()
    except Exception:
        pass  # non-fatal


def _restore_user_from_mongo(username, password):
    try:
        from .models import MongoUser
        from django.contrib.auth.hashers import check_password

        mu = MongoUser.objects(username=username).first()
        if not mu:
            # by email
            mu = MongoUser.objects(email=username).first()
        if not mu or not check_password(password, mu.password):
            return None

        existing = User.objects.filter(pk=mu.django_id).first()
        if existing:
            # Slot is taken — update it to match MongoDB (handles ID conflicts)
            existing.username     = mu.username
            existing.email        = mu.email
            existing.first_name   = mu.first_name
            existing.last_name    = mu.last_name
            existing.password     = mu.password
            existing.is_active    = mu.is_active
            existing.is_staff     = mu.is_staff
            existing.is_superuser = mu.is_superuser
            existing.save()
        else:
            user = User(pk=mu.django_id)
            user.username     = mu.username
            user.email        = mu.email
            user.first_name   = mu.first_name
            user.last_name    = mu.last_name
            user.password     = mu.password
            user.is_active    = mu.is_active
            user.is_staff     = mu.is_staff
            user.is_superuser = mu.is_superuser
            user.date_joined  = mu.date_joined
            user.save(force_insert=True)

        return authenticate(request=None, username=mu.username, password=password)
    except Exception:
        return None


def _send_verification_email(request, to_email, first_name, code):
    from django.templatetags.static import static as static_url
    logo_src = request.build_absolute_uri(static_url('img/logo.png'))
    html_body = render_to_string('accounts/email_verify.html', {
        'first_name': first_name,
        'code':       code,
        'logo_src':   logo_src,
    })
    subject = 'Your Velvet Steel Verification Code'
    host_user  = getattr(settings, 'EMAIL_HOST_USER', '')
    from_email = host_user or getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@velvetsteel.ph')
    display_from = f'Velvet Steel Barbershop <{from_email}>'
    msg = EmailMultiAlternatives(subject, f'Your verification code is: {code}', display_from, [to_email])
    msg.attach_alternative(html_body, 'text/html')
    msg.send(fail_silently=False)


# ── forms ────────────────────────────────────────────────────────────────────

class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=30,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name  = forms.CharField(max_length=30,  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone      = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+63 9XX XXX XXXX'}))
    password1  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already taken.')
        return username

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


# ── views ────────────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            # Remove any old pending verifications for this email/username
            try:
                EmailVerification.objects(email=email).delete()
                EmailVerification.objects(username=username).delete()
            except Exception:
                pass
            # Generate 6-digit code
            code = ''.join(random.choices(string.digits, k=6))
            expires = datetime.utcnow() + timedelta(minutes=15)
            ev = EmailVerification(
                email=email,
                username=username,
                code=code,
                expires_at=expires,
            )
            ev.save()
            # Store pending form data securely in session (never persisted to DB)
            request.session['pending_register'] = {
                'username':   username,
                'email':      email,
                'password':   form.cleaned_data['password1'],
                'first_name': form.cleaned_data['first_name'],
                'last_name':  form.cleaned_data['last_name'],
                'phone':      form.cleaned_data.get('phone', ''),
            }
            # Send verification email
            try:
                _send_verification_email(request, email, form.cleaned_data['first_name'], code)
            except Exception as e:
                messages.error(request, f'Could not send verification email: {e}')
                return render(request, 'accounts/register.html', {'form': form})
            messages.info(request, f'A 6-digit verification code was sent to {email}. Check your inbox.')
            return redirect('verify_email')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request):
    pending = request.session.get('pending_register')
    if not pending:
        return redirect('register')
    email = pending['email']
    try:
        ev = EmailVerification.objects(email=email).order_by('-id').first()
    except Exception:
        ev = None
    if not ev:
        messages.error(request, 'No pending verification found. Please register again.')
        return redirect('register')
    if request.method == 'POST':
        entered = request.POST.get('code', '').strip()
        # Check expiry
        if datetime.utcnow() > ev.expires_at:
            ev.delete()
            request.session.pop('pending_register', None)
            messages.error(request, 'The code has expired. Please register again.')
            return redirect('register')
        # Increment attempts (brute-force protection)
        ev.attempts += 1
        ev.save()
        if ev.attempts > 10:
            ev.delete()
            request.session.pop('pending_register', None)
            messages.error(request, 'Too many incorrect attempts. Please register again.')
            return redirect('register')
        if entered != ev.code:
            remaining = max(0, 10 - ev.attempts)
            messages.error(request, f'Incorrect code. {remaining} attempt(s) remaining.')
            return render(request, 'accounts/verify_email.html', {
                'email':     email,
                'remaining': remaining,
            })
        # Code is correct — create the account
        try:
            dj_user = User.objects.create_user(
                username=pending['username'],
                email=pending['email'],
                password=pending['password'],
                first_name=pending['first_name'],
                last_name=pending['last_name'],
            )
            _persist_user_to_mongo(dj_user)
            try:
                profile = UserProfile(user_id=dj_user.pk, phone=pending.get('phone', ''))
                profile.save()
            except Exception:
                pass
        except Exception as e:
            messages.error(request, f'Account creation failed: {e}')
            return redirect('register')
        ev.delete()
        request.session.pop('pending_register', None)
        dj_user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, dj_user)
        messages.success(request, f'Welcome, {dj_user.first_name}! Your email has been verified.')
        return redirect('home')
    return render(request, 'accounts/verify_email.html', {'email': email, 'remaining': 10})


def resend_code_view(request):
    pending = request.session.get('pending_register')
    if not pending:
        return redirect('register')
    email = pending['email']
    try:
        ev = EmailVerification.objects(email=email).order_by('-id').first()
    except Exception:
        ev = None
    if not ev:
        return redirect('register')
    # Issue a fresh code and reset expiry/attempts
    ev.code = ''.join(random.choices(string.digits, k=6))
    ev.expires_at = datetime.utcnow() + timedelta(minutes=15)
    ev.attempts = 0
    ev.save()
    try:
        _send_verification_email(request, email, pending['first_name'], ev.code)
        messages.success(request, f'A new code has been sent to {email}.')
    except Exception as e:
        messages.error(request, f'Could not resend code: {e}')
    return redirect('verify_email')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if not user:
                try:
                    user_by_email = User.objects.get(email=username)
                    user = authenticate(request, username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    pass

            if not user:
                user = _restore_user_from_mongo(username, password)

            if user:
                login(request, user)
                _get_or_create_profile(user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('user_dashboard' if user.is_staff else 'home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def user_dashboard(request):
    from reservations.models import Reservation, Testimonial

    profile = _get_or_create_profile(request.user)

    try:
        user_reservations = list(
            Reservation.objects(customer_id=request.user.pk).order_by('-created_at')
        )
    except Exception:
        user_reservations = []

    upcoming     = [r for r in user_reservations if r.status in ['pending', 'confirmed']]
    past         = [r for r in user_reservations if r.status in ['completed', 'cancelled']]
    completed    = [r for r in user_reservations if r.status == 'completed']
    total_visits = len(completed)
    total_spent  = sum(float(r.total_price or 0) for r in completed)

    try:
        my_testimonials = list(
            Testimonial.objects(customer_username=request.user.username).order_by('-created_at')
        )
    except Exception:
        my_testimonials = []

    reviewed_ids = {t.reservation_id for t in my_testimonials if t.reservation_id}
    reviewable   = [r for r in completed if str(r.pk) not in reviewed_ids][:5]

    return render(request, 'accounts/dashboard.html', {
        'profile':           profile,
        'upcoming':          upcoming[:5],
        'past':              past[:5],
        'total_visits':      total_visits,
        'total_spent':       total_spent,
        'reservation_count': len(user_reservations),
        'user':              request.user,
        'my_testimonials':   my_testimonials,
        'reviewable':        reviewable,
    })


@login_required
def profile_view(request):
    import base64
    profile = _get_or_create_profile(request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name  = request.POST.get('last_name', '')
        request.user.email      = request.POST.get('email', '')
        request.user.save()
        _persist_user_to_mongo(request.user)
        try:
            profile.phone = request.POST.get('phone', '')
            profile.city  = request.POST.get('city', '')
            photo_file = request.FILES.get('photo')
            if photo_file:
                raw  = photo_file.read()
                mime = photo_file.content_type or 'image/jpeg'
                b64  = base64.b64encode(raw).decode()
                profile.photo = f"data:{mime};base64,{b64}"
            profile.save()
        except Exception:
            pass
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'profile': profile})