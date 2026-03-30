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
        barber_id        = request.POST.get('barber', '').strip()
        haircut_style_id = request.POST.get('haircut_style', '').strip()
        appointment_date = request.POST.get('appointment_date', '').strip()
        appointment_time = request.POST.get('appointment_time', '').strip()
        notes            = request.POST.get('notes', '').strip()

        errors        = []
        barber        = None
        haircut_style = None

        if barber_id:
            try:
                barber = Barber.objects(id=barber_id).first()
            except Exception:
                barber = None

        if haircut_style_id:
            try:
                haircut_style = HaircutStyle.objects(id=haircut_style_id).first()
            except Exception:
                haircut_style = None

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
            try:
                existing = Reservation.objects(
                    barber=barber,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status__in=['pending', 'confirmed'],
                ).first()
                if existing:
                    errors.append('This time slot is already booked. Please choose another.')
            except Exception:
                pass

        if errors:
            for err in errors:
                messages.error(request, err)
            styles  = HaircutStyle.objects(is_active=True).order_by('category', 'price')
            barbers = Barber.objects(is_active=True)
            return render(request, 'reservations/book.html', {'styles': styles, 'barbers': barbers})

        try:
            service = Service.objects(is_active=True).first()
        except Exception:
            service = None

        total_price = None
        if haircut_style and haircut_style.price is not None:
            total_price = haircut_style.price
        elif service and service.price is not None:
            total_price = service.price
        else:
            total_price = 0

        reservation = Reservation(
            customer_id=request.user.pk,
            customer_username=request.user.username,
            customer_name=request.user.get_full_name() or request.user.username,
            barber=barber,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            total_price=total_price,
        )

        import random, string
        reservation.confirmation_code = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )

        try:
            reservation.save()
        except Exception as e:
            messages.error(request, f'Could not save reservation. Please try again. ({e})')
            styles  = HaircutStyle.objects(is_active=True).order_by('category', 'price')
            barbers = Barber.objects(is_active=True)
            return render(request, 'reservations/book.html', {'styles': styles, 'barbers': barbers})

        messages.success(request, 'Reservation confirmed! Your code: ' + reservation.confirmation_code)
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
    try:
        reservation = Reservation.objects(id=pk).first()
        if reservation and not request.user.is_staff:
            if reservation.customer_id != request.user.pk:
                reservation = None
    except Exception:
        reservation = None
    if not reservation:
        messages.error(request, 'Reservation not found.')
        return redirect('my_reservations')
    return render(request, 'reservations/detail.html', {'reservation': reservation})


@login_required
def cancel_reservation(request, pk):
    try:
        reservation = Reservation.objects(id=pk).first()
        if reservation and reservation.customer_id != request.user.pk:
            reservation = None
    except Exception:
        reservation = None
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

    try:
        barber = Barber.objects(id=barber_id).first()
    except Exception:
        return JsonResponse({'slots': []})

    if not barber:
        return JsonResponse({'slots': []})

    try:
        booked_reservations = Reservation.objects(
            barber=barber,
            appointment_date=date_str,
            status__in=['pending', 'confirmed'],
        )
        booked_times = set(r.appointment_time for r in booked_reservations)
    except Exception:
        booked_times = set()

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
        service_id = request.POST.get('service', '').strip()
        service    = None
        if service_id:
            try:
                service = Service.objects(id=service_id).first()
            except Exception:
                pass

        testimonial = Testimonial(
            customer_id=request.user.pk,
            customer_name=request.user.get_full_name() or request.user.username,
            rating=int(rating),
            comment=comment,
            service=service,
        )
        try:
            testimonial.save()
            messages.success(request, 'Thank you for your review! It will appear once approved.')
        except Exception:
            messages.error(request, 'Could not submit review. Please try again.')
    return redirect('home')