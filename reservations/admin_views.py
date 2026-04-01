from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from functools import wraps
from .models import Reservation, Service, Barber, Testimonial, GalleryImage, HaircutStyle
from accounts.models import UserProfile
import datetime
import base64


def _customer_photos(reservations):
    usernames = {r.customer_username for r in reservations if r.customer_username}
    photos = {}
    for uname in usernames:
        try:
            dj = User.objects.filter(username=uname).first()
            if dj:
                prof = UserProfile.objects(user_id=dj.pk).first()
                if prof and prof.photo:
                    photos[uname] = prof.photo
        except Exception:
            pass
    return photos


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_staff:
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    today = timezone.now().date().isoformat()
    today_obj = timezone.now().date()

    total_reservations = Reservation.objects().count()
    today_reservations = Reservation.objects(appointment_date=today).count()
    pending   = Reservation.objects(status='pending').count()
    confirmed = Reservation.objects(status='confirmed').count()
    completed = Reservation.objects(status='completed').count()
    cancelled = Reservation.objects(status='cancelled').count()

    completed_today = Reservation.objects(appointment_date=today, status='completed')
    revenue_today   = sum(float(r.total_price or 0) for r in completed_today)

    month_start = today_obj.replace(day=1).isoformat()
    completed_month = Reservation.objects(
        appointment_date__gte=month_start,
        appointment_date__lte=today,
        status='completed',
    )
    revenue_month = sum(float(r.total_price or 0) for r in completed_month)

    recent_reservations  = list(Reservation.objects().order_by('-created_at')[:10])
    pending_testimonials = Testimonial.objects(is_approved=False).count()
    photos = _customer_photos(recent_reservations)
    for res in recent_reservations:
        res._cust_photo = photos.get(res.customer_username, '')

    return render(request, 'admin_panel/dashboard.html', {
        'total_reservations':  total_reservations,
        'today_reservations':  today_reservations,
        'pending':   pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
        'revenue_today':  revenue_today,
        'revenue_month':  revenue_month,
        'recent_reservations':  recent_reservations,
        'pending_testimonials': pending_testimonials,
        'today': today_obj,
    })


@admin_required
def admin_reservations(request):
    status_filter = request.GET.get('status', '')
    date_filter   = request.GET.get('date', '')
    qs = Reservation.objects().order_by('-created_at')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if date_filter:
        qs = qs.filter(appointment_date=date_filter)
    reservations = list(qs)
    photos = _customer_photos(reservations)
    for res in reservations:
        res._cust_photo = photos.get(res.customer_username, '')
    return render(request, 'admin_panel/reservations.html', {
        'reservations':  reservations,
        'status_filter': status_filter,
        'date_filter':   date_filter,
    })


@admin_required
def admin_bulk_delete_reservations(request):
    if request.method == 'POST':
        pks = request.POST.getlist('pks')
        deleted = 0
        for pk in pks:
            try:
                res = Reservation.objects(id=pk).first()
                if res:
                    res.delete()
                    deleted += 1
            except Exception:
                pass
        if deleted:
            messages.success(request, f'{deleted} reservation(s) deleted successfully.')
        else:
            messages.warning(request, 'No reservations were deleted.')
    return redirect('admin_reservations')


@admin_required
def admin_update_reservation(request, pk):
    try:
        reservation = Reservation.objects(id=pk).first()
    except Exception:
        reservation = None
    if not reservation:
        messages.error(request, 'Reservation not found.')
        return redirect('admin_reservations')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Reservation.STATUS_CHOICES]
        if new_status in valid:
            reservation.status = new_status
            reservation.save()
            messages.success(
                request,
                f'Reservation {reservation.confirmation_code} updated to {new_status}.'
            )
    return redirect('admin_reservations')


@admin_required
def admin_barbers(request):
    return render(request, 'admin_panel/barbers.html', {
        'barbers': Barber.objects().all()
    })


@admin_required
def admin_barber_add(request):
    from .forms import BarberForm
    if request.method == 'POST':
        form = BarberForm(request.POST, request.FILES)
        if form.is_valid():
            data       = form.cleaned_data.copy()
            photo_file = data.pop('photo', None)
            barber     = Barber(**data)
            if photo_file:
                barber.photo = _image_to_data_uri(photo_file)
            try:
                barber.save()
                messages.success(request, f'"{barber.name}" added successfully.')
                return redirect('admin_barbers')
            except Exception as e:
                messages.error(request, f'Could not save: {e}')
    else:
        form = BarberForm()
    return render(request, 'admin_panel/barber_form.html', {
        'form': form, 'action': 'Add',
    })


@admin_required
def admin_barber_edit(request, pk):
    from .forms import BarberForm
    try:
        barber = Barber.objects(id=pk).first()
    except Exception:
        barber = None
    if not barber:
        messages.error(request, 'Barber not found.')
        return redirect('admin_barbers')

    if request.method == 'POST':
        form = BarberForm(request.POST, request.FILES)
        if form.is_valid():
            data       = form.cleaned_data.copy()
            photo_file = data.pop('photo', None)
            for k, v in data.items():
                setattr(barber, k, v)
            if photo_file:
                barber.photo = _image_to_data_uri(photo_file)
            try:
                barber.save()
                messages.success(request, f'"{barber.name}" updated successfully.')
                return redirect('admin_barbers')
            except Exception as e:
                messages.error(request, f'Could not save: {e}')
    else:
        form = BarberForm(initial={
            'name':             barber.name,
            'specialty':        barber.specialty,
            'bio':              barber.bio,
            'experience_years': barber.experience_years,
            'rating':           barber.rating,
            'instagram':        barber.instagram,
            'is_active':        barber.is_active,
        })
    return render(request, 'admin_panel/barber_form.html', {
        'form': form, 'action': 'Edit', 'barber': barber,
    })


@admin_required
def admin_barber_delete(request, pk):
    try:
        barber = Barber.objects(id=pk).first()
    except Exception:
        barber = None
    if barber and request.method == 'POST':
        name = barber.name
        barber.delete()
        messages.success(request, f'"{name}" deleted.')
    return redirect('admin_barbers')


@admin_required
def admin_testimonials(request):
    return render(request, 'admin_panel/testimonials.html', {
        'testimonials': Testimonial.objects().order_by('-created_at')
    })


@admin_required
def approve_testimonial(request, pk):
    try:
        testimonial = Testimonial.objects(id=pk).first()
    except Exception:
        testimonial = None
    if testimonial:
        testimonial.is_approved = not testimonial.is_approved
        testimonial.save()
    return redirect('admin_testimonials')


@admin_required
def admin_analytics(request):
    today = timezone.now().date()
    days_data = []
    for i in range(6, -1, -1):
        day     = today - datetime.timedelta(days=i)
        day_str = day.isoformat()
        count   = Reservation.objects(appointment_date=day_str).count()
        done    = Reservation.objects(appointment_date=day_str, status='completed')
        revenue = sum(float(r.total_price or 0) for r in done)
        days_data.append({
            'date': day.strftime('%b %d'),
            'count': count,
            'revenue': revenue,
        })

    from collections import Counter
    svc_counter = Counter()
    for r in Reservation.objects().only('service'):
        if r.service:
            svc_counter[str(r.service.id)] += 1

    service_stats = []
    for svc_id, count in svc_counter.most_common(5):
        try:
            svc = Service.objects(id=svc_id).first()
        except Exception:
            svc = None
        if svc:
            svc.booking_count = count
            service_stats.append(svc)

    barber_counter = Counter()
    for r in Reservation.objects().only('barber'):
        if r.barber:
            barber_counter[str(r.barber.id)] += 1

    barber_stats = []
    for barber in Barber.objects().all():
        barber.booking_count = barber_counter.get(str(barber.id), 0)
        barber_stats.append(barber)
    barber_stats.sort(key=lambda b: b.booking_count, reverse=True)

    return render(request, 'admin_panel/analytics.html', {
        'days_data':     days_data,
        'service_stats': service_stats,
        'barber_stats':  barber_stats,
    })


@admin_required
def admin_haircut_styles(request):
    category_filter = request.GET.get('category', '')
    styles = HaircutStyle.objects().all()
    if category_filter:
        styles = styles.filter(category=category_filter)
    return render(request, 'admin_panel/haircut_styles.html', {
        'styles':          styles,
        'categories':      HaircutStyle.CATEGORY_CHOICES,
        'category_filter': category_filter,
    })


def _image_to_data_uri(image_file):
    if not image_file:
        return None
    mime = getattr(image_file, 'content_type', None) or 'image/jpeg'
    b64  = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime};base64,{b64}"


@admin_required
def admin_haircut_style_add(request):
    from .forms import HaircutStyleForm
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            data       = form.cleaned_data.copy()
            image_file = data.pop('image', None)
            style      = HaircutStyle(**data)
            if image_file:
                style.image = _image_to_data_uri(image_file)
            try:
                style.save()
                messages.success(request, f'"{style.name}" added successfully.')
                return redirect('admin_haircut_styles')
            except Exception as e:
                messages.error(request, f'Could not save: {e}')
    else:
        form = HaircutStyleForm()
    return render(request, 'admin_panel/haircut_style_form.html', {
        'form': form, 'action': 'Add',
    })


@admin_required
def admin_haircut_style_edit(request, pk):
    from .forms import HaircutStyleForm
    try:
        style = HaircutStyle.objects(id=pk).first()
    except Exception:
        style = None
    if not style:
        messages.error(request, 'Style not found.')
        return redirect('admin_haircut_styles')

    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            data       = form.cleaned_data.copy()
            image_file = data.pop('image', None)
            for k, v in data.items():
                setattr(style, k, v)
            if image_file:
                style.image = _image_to_data_uri(image_file)
            try:
                style.save()
                messages.success(request, f'"{style.name}" updated successfully.')
                return redirect('admin_haircut_styles')
            except Exception as e:
                messages.error(request, f'Could not save: {e}')
    else:
        form = HaircutStyleForm(initial={
            'name':        style.name,
            'category':    style.category,
            'description': style.description,
            'price':       style.price,
            'is_active':   style.is_active,
        })
    return render(request, 'admin_panel/haircut_style_form.html', {
        'form': form, 'action': 'Edit', 'style': style,
    })


@admin_required
def admin_haircut_style_delete(request, pk):
    try:
        style = HaircutStyle.objects(id=pk).first()
    except Exception:
        style = None
    if style and request.method == 'POST':
        name = style.name
        style.delete()
        messages.success(request, f'"{name}" deleted.')
    return redirect('admin_haircut_styles')


@admin_required
def admin_availability(request):
    barbers = Barber.objects(is_active=True)
    return render(request, 'admin_panel/availability.html', {
        'barbers': barbers,
    })


@admin_required
def admin_services(request):
    services = Service.objects().order_by('category', 'price')
    return render(request, 'admin_panel/services.html', {'services': services})


@admin_required
def admin_service_add(request):
    from .forms import ServiceForm
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            data       = form.cleaned_data.copy()
            image_file = data.pop('image', None)
            svc = Service(
                name=data['name'],
                category=data['category'],
                description=data.get('description', ''),
                price=data['price'],
                duration_minutes=data.get('duration_minutes', 30),
                is_active=data.get('is_active', True),
            )
            if image_file:
                svc.image = _image_to_data_uri(image_file)
            try:
                svc.save()
                messages.success(request, f'"{svc.name}" added successfully.')
                return redirect('admin_services')
            except Exception as e:
                messages.error(request, f'Could not save: {e}')
    else:
        form = ServiceForm()
    return render(request, 'admin_panel/service_form.html', {'form': form, 'action': 'Add'})


@admin_required
def admin_service_edit(request, pk):
    from .forms import ServiceForm
    try:
        svc = Service.objects(id=pk).first()
    except Exception:
        svc = None
    if not svc:
        messages.error(request, 'Service not found.')
        return redirect('admin_services')
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            data       = form.cleaned_data.copy()
            image_file = data.pop('image', None)
            for k, v in data.items():
                setattr(svc, k, v)
            if image_file:
                svc.image = _image_to_data_uri(image_file)
            try:
                svc.save()
                messages.success(request, f'"{svc.name}" updated successfully.')
                return redirect('admin_services')
            except Exception as e:
                messages.error(request, f'Could not save: {e}')
    else:
        form = ServiceForm(initial={
            'name':             svc.name,
            'category':         svc.category,
            'description':      svc.description,
            'price':            svc.price,
            'duration_minutes': svc.duration_minutes,
            'is_active':        svc.is_active,
        })
    return render(request, 'admin_panel/service_form.html', {
        'form': form, 'action': 'Edit', 'svc': svc,
    })


@admin_required
def admin_service_delete(request, pk):
    try:
        svc = Service.objects(id=pk).first()
    except Exception:
        svc = None
    if svc and request.method == 'POST':
        name = svc.name
        svc.delete()
        messages.success(request, f'"{name}" deleted.')
    return redirect('admin_services')