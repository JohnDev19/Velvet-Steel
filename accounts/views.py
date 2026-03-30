from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django import forms
from .models import UserProfile


class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+63 9XX XXX XXXX'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

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


def _get_or_create_profile(user):
    """Get or create a MongoEngine UserProfile for a Django auth user."""
    profile = UserProfile.objects(user_id=user.pk).first()
    if not profile:
        profile = UserProfile(user_id=user.pk)
        profile.save()
    return profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            profile = UserProfile(
                user_id=user.pk,
                phone=form.cleaned_data.get('phone', ''),
            )
            profile.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Your account has been created.')
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
                    user = None
            
            if user:
                login(request, user)
                _get_or_create_profile(user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                if user.is_staff:
                    next_url = request.GET.get('next', 'user_dashboard')
                return redirect(next_url)
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
    """User dashboard showing their reservations and profile overview."""
    from reservations.models import Reservation
    profile = _get_or_create_profile(request.user)
    
    user_reservations = Reservation.objects(user_id=request.user.pk).order_by('-created_at')
    upcoming = [r for r in user_reservations if r.status in ['pending', 'confirmed']]
    past = [r for r in user_reservations if r.status in ['completed', 'cancelled']]
    
    total_visits = len([r for r in user_reservations if r.status == 'completed'])
    total_spent = sum(float(r.total_price or 0) for r in user_reservations if r.status == 'completed')
    
    context = {
        'profile': profile,
        'upcoming': upcoming[:5],
        'past': past[:5],
        'total_visits': total_visits,
        'total_spent': total_spent,
        'reservation_count': len(user_reservations),
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    profile = _get_or_create_profile(request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        profile.phone = request.POST.get('phone', '')
        profile.city = request.POST.get('city', '')
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'profile': profile})
