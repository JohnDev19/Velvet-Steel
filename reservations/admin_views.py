from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from .models import Reservation, Service, Barber, Testimonial, GalleryImage
import datetime


@staff_member_required
def admin_dashboard(request):
    today = timezone.now().date()
    total_reservations = Reservation.objects.count()
    today_reservations = Reservation.objects.filter(appointment_date=today).count()
    pending = Reservation.objects.filter(status='pending').count()
    confirmed = Reservation.objects.filter(status='confirmed').count()
    completed = Reservation.objects.filter(status='completed').count()
    cancelled = Reservation.objects.filter(status='cancelled').count()
    revenue_today = Reservation.objects.filter(
        appointment_date=today, status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    revenue_month = Reservation.objects.filter(
        appointment_date__year=today.year,
        appointment_date__month=today.month,
        status='completed'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    recent_reservations = Reservation.objects.select_related(
        'customer', 'barber', 'service'
    ).order_by('-created_at')[:10]
    pending_testimonials = Testimonial.objects.filter(is_approved=False).count()

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
        'today': today,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@staff_member_required
def admin_reservations(request):
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    reservations = Reservation.objects.select_related('customer', 'barber', 'service').order_by('-created_at')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    if date_filter:
        reservations = reservations.filter(appointment_date=date_filter)
    return render(request, 'admin_panel/reservations.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'date_filter': date_filter,
    })


@staff_member_required
def admin_update_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Reservation.STATUS_CHOICES):
            reservation.status = new_status
            reservation.save()
            messages.success(request, f'Reservation #{reservation.confirmation_code} updated to {new_status}.')
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
    testimonials = Testimonial.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/testimonials.html', {'testimonials': testimonials})


@staff_member_required
def approve_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.is_approved = not testimonial.is_approved
    testimonial.save()
    return redirect('admin_testimonials')


@staff_member_required
def admin_analytics(request):
    today = timezone.now().date()
    # Last 7 days data
    days_data = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        count = Reservation.objects.filter(appointment_date=day).count()
        revenue = Reservation.objects.filter(
            appointment_date=day, status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        days_data.append({'date': day.strftime('%b %d'), 'count': count, 'revenue': float(revenue)})

    service_stats = Service.objects.annotate(
        booking_count=Count('reservation')
    ).order_by('-booking_count')[:5]

    barber_stats = Barber.objects.annotate(
        booking_count=Count('reservations')
    ).order_by('-booking_count')

    context = {
        'days_data': days_data,
        'service_stats': service_stats,
        'barber_stats': barber_stats,
    }
    return render(request, 'admin_panel/analytics.html', context)
