from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Reservation, Service, Barber, Testimonial, GalleryImage, HaircutStyle
import datetime


@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date().isoformat()
    today_obj = timezone.now().date()

    total_reservations = Reservation.objects.count()
    today_reservations = Reservation.objects(appointment_date=today).count()
    pending = Reservation.objects(status='pending').count()
    confirmed = Reservation.objects(status='confirmed').count()
    completed = Reservation.objects(status='completed').count()
    cancelled = Reservation.objects(status='cancelled').count()

    completed_today = Reservation.objects(appointment_date=today, status='completed')
    revenue_today = sum(float(r.total_price or 0) for r in completed_today)

    month_start = today_obj.replace(day=1).isoformat()
    completed_month = Reservation.objects(
        appointment_date__gte=month_start,
        appointment_date__lte=today,
        status='completed'
    )
    revenue_month = sum(float(r.total_price or 0) for r in completed_month)

    recent_reservations = Reservation.objects.order_by('-created_at')[:10]
    pending_testimonials = Testimonial.objects(is_approved=False).count()

    context = {
        'total_reservations': total_reservations,
        'today_reservations': today_reservations,
        'pending': pending,
        'confirmed': confirmed,
        'completed': completed,
        'cancelled': cancelled,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'recent_reservations': recent_reservations,
        'pending_testimonials': pending_testimonials,
        'today': today_obj,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@staff_member_required
def admin_reservations(request):
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    qs = Reservation.objects.order_by('-created_at')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if date_filter:
        qs = qs.filter(appointment_date=date_filter)

    return render(request, 'admin_panel/reservations.html', {
        'reservations': qs,
        'status_filter': status_filter,
        'date_filter': date_filter,
    })


@staff_member_required
def admin_update_reservation(request, pk):
    reservation = Reservation.objects(id=pk).first()
    if not reservation:
        messages.error(request, 'Reservation not found.')
        return redirect('admin_reservations')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid = [s[0] for s in Reservation.STATUS_CHOICES]
        if new_status in valid:
            reservation.status = new_status
            reservation.save()
            messages.success(request, f'Reservation {reservation.confirmation_code} updated to {new_status}.')
    return redirect('admin_reservations')


@staff_member_required
def admin_services(request):
    services = Service.objects.all()
    return render(request, 'admin_panel/services.html', {'services': services})


@staff_member_required
def admin_barbers(request):
    barbers = Barber.objects.all()
    return render(request, 'admin_panel/barbers.html', {'barbers': barbers})


@staff_member_required
def admin_testimonials(request):
    testimonials = Testimonial.objects.order_by('-created_at')
    return render(request, 'admin_panel/testimonials.html', {'testimonials': testimonials})


@staff_member_required
def approve_testimonial(request, pk):
    testimonial = Testimonial.objects(id=pk).first()
    if testimonial:
        testimonial.is_approved = not testimonial.is_approved
        testimonial.save()
    return redirect('admin_testimonials')


@staff_member_required
def admin_analytics(request):
    today = timezone.now().date()
    days_data = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_str = day.isoformat()
        count = Reservation.objects(appointment_date=day_str).count()
        completed = Reservation.objects(appointment_date=day_str, status='completed')
        revenue = sum(float(r.total_price or 0) for r in completed)
        days_data.append({'date': day.strftime('%b %d'), 'count': count, 'revenue': revenue})

    # Top services by booking count
    from collections import Counter
    all_res = Reservation.objects.only('service')
    service_counter = Counter()
    for r in all_res:
        if r.service:
            service_counter[str(r.service.id)] += 1

    service_stats = []
    for svc_id, count in service_counter.most_common(5):
        svc = Service.objects(id=svc_id).first()
        if svc:
            svc.booking_count = count
            service_stats.append(svc)

    # Barber stats
    barber_counter = Counter()
    for r in Reservation.objects.only('barber'):
        if r.barber:
            barber_counter[str(r.barber.id)] += 1

    barber_stats = []
    for barber in Barber.objects.all():
        barber.booking_count = barber_counter.get(str(barber.id), 0)
        barber_stats.append(barber)
    barber_stats.sort(key=lambda b: b.booking_count, reverse=True)

    return render(request, 'admin_panel/analytics.html', {
        'days_data': days_data,
        'service_stats': service_stats,
        'barber_stats': barber_stats,
    })


@staff_member_required
def admin_haircut_styles(request):
    category_filter = request.GET.get('category', '')
    styles = HaircutStyle.objects.all()
    if category_filter:
        styles = styles.filter(category=category_filter)
    categories = HaircutStyle.CATEGORY_CHOICES
    return render(request, 'admin_panel/haircut_styles.html', {
        'styles': styles,
        'categories': categories,
        'category_filter': category_filter,
    })


@staff_member_required
def admin_haircut_style_add(request):
    from .forms import HaircutStyleForm
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            style = HaircutStyle(**form.cleaned_data)
            style.save()
            messages.success(request, 'Haircut style added successfully.')
            return redirect('admin_haircut_styles')
    else:
        form = HaircutStyleForm()
    return render(request, 'admin_panel/haircut_style_form.html', {'form': form, 'action': 'Add'})


@staff_member_required
def admin_haircut_style_edit(request, pk):
    from .forms import HaircutStyleForm
    style = HaircutStyle.objects(id=pk).first()
    if not style:
        messages.error(request, 'Style not found.')
        return redirect('admin_haircut_styles')
    if request.method == 'POST':
        form = HaircutStyleForm(request.POST, request.FILES)
        if form.is_valid():
            for k, v in form.cleaned_data.items():
                setattr(style, k, v)
            style.save()
            messages.success(request, f'"{style.name}" updated successfully.')
            return redirect('admin_haircut_styles')
    else:
        form = HaircutStyleForm(initial={
            'name': style.name,
            'category': style.category,
            'description': style.description,
            'price': style.price,
            'is_active': style.is_active,
        })
    return render(request, 'admin_panel/haircut_style_form.html', {
        'form': form, 'action': 'Edit', 'style': style
    })


@staff_member_required
def admin_haircut_style_delete(request, pk):
    style = HaircutStyle.objects(id=pk).first()
    if style and request.method == 'POST':
        name = style.name
        style.delete()
        messages.success(request, f'"{name}" deleted.')
    return redirect('admin_haircut_styles')