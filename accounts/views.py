from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from .models import UserProfile


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

        if not User.objects.filter(pk=mu.django_id).exists():
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
            dj_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            _persist_user_to_mongo(dj_user)
            try:
                profile = UserProfile(
                    user_id=dj_user.pk,
                    phone=form.cleaned_data.get('phone', ''),
                )
                profile.save()
            except Exception:
                pass
            login(request, dj_user)
            messages.success(request, f'Welcome, {dj_user.first_name}! Your account has been created.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


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
            profile.save()
        except Exception:
            pass
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'profile': profile})