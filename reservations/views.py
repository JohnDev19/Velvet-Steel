from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Reservation, Service, Barber, Testimonial, HaircutStyle
import datetime


@login_required
def book_reservation(request):
    if request.method == 'POST':
        barber_id          = request.POST.get('barber')
        haircut_style_id   = request.POST.get('haircut_style')
        appointment_date   = request.POST.get('appointment_date')
        appointment_time   = request.POST.get('appointment_time')
        notes              = request.POST.get('notes', '')

        errors = []
        barber        = Barber.objects(id=barber_id).first()        if barber_id        else None
        haircut_style = HaircutStyle.objects(id=haircut_style_id).first() if haircut_style_id else None

        if not barber:
            errors.append('Please select a valid barber.')
        if not haircut_style:
            errors.append('Please select a haircut style.')
        if not appointment_date:
            errors.append('Please select a date.')
        if not appointment_time:
            errors.append('Please select a time.')

        if not errors:
            try:
                date_obj = datetime.date.fromisoformat(appointment_date)
                if date_obj < timezone.now().date():
                    errors.append('Please select today or a future date.')
            except ValueError:
                errors.append('Invalid date format.')

        if not errors:
            existing = Reservation.objects(
                barber=barber,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['pending', 'confirmed'],
            ).first()
            if existing:
                errors.append('This time slot is already booked. Please choose another.')

        if errors:
            for err in errors:
                messages.error(request, err)
        else:
            default_service = Service.objects(is_active=True).first()

            reservation = Reservation(
                customer_id=request.user.pk,
                customer_username=request.user.username,
                customer_name=request.user.get_full_name() or request.user.username,
                barber=barber,
                service=default_service,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                notes=notes,
                total_price=haircut_style.price,
            )
            reservation.save()
            messages.success(request, f'Reservation confirmed! Your code: {reservation.confirmation_code}')
            return redirect('reservation_detail', pk=str(reservation.pk))

    styles  = HaircutStyle.objects(is_active=True).order_by('category', 'price')
    barbers = Barber.objects(is_active=True)
    return render(request, 'reservations/book.html', {
        'styles':  styles,
        'barbers': barbers,
    })


@login_required
def my_reservations(request):
    reservations = Reservation.objects(customer_id=request.user.pk).order_by('-created_at')
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})


@login_required
def reservation_detail(request, pk):
    reservation = Reservation.objects(id=pk, customer_id=request.user.pk).first()
    if not reservation:
        messages.error(request, 'Reservation not found.')
        return redirect('my_reservations')
    return render(request, 'reservations/detail.html', {'reservation': reservation})


@login_required
def cancel_reservation(request, pk):
    reservation = Reservation.objects(id=pk, customer_id=request.user.pk).first()
    if reservation and reservation.status in ['pending', 'confirmed']:
        try:
            date_obj = datetime.date.fromisoformat(reservation.appointment_date)
            if date_obj >= timezone.now().date():
                reservation.status = 'cancelled'
                reservation.save()
                messages.success(request, 'Reservation cancelled successfully.')
            else:
                messages.error(request, 'Cannot cancel past reservations.')
        except Exception:
            messages.error(request, 'Could not cancel reservation.')
    return redirect('my_reservations')


def get_available_slots(request):
    barber_id = request.GET.get('barber_id', '').strip()
    date_str  = request.GET.get('date', '').strip()

    if not barber_id or not date_str:
        return JsonResponse({'slots': []})

    barber = Barber.objects(id=barber_id).first()
    if not barber:
        return JsonResponse({'slots': []})

    booked_reservations = Reservation.objects(
        barber=barber,
        appointment_date=date_str,
        status__in=['pending', 'confirmed'],
    )
    booked_times = set(r.appointment_time for r in booked_reservations)

    slots = []
    for hour in range(8, 20):
        for minute in [0, 30]:
            t   = datetime.time(hour, minute)
            val = t.strftime('%H:%M')
            if val not in booked_times:
                slots.append({'value': val, 'label': t.strftime('%I:%M %p')})

    return JsonResponse({'slots': slots})


@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        rating     = request.POST.get('rating', 5)
        comment    = request.POST.get('comment', '')
        service_id = request.POST.get('service')
        service    = Service.objects(id=service_id).first() if service_id else None

        testimonial = Testimonial(
            customer_id=request.user.pk,
            customer_name=request.user.get_full_name() or request.user.username,
            rating=int(rating),
            comment=comment,
            service=service,
        )
        testimonial.save()
        messages.success(request, 'Thank you for your review! It will appear once approved.')
    return redirect('home')