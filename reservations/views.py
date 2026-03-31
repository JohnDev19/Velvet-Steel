from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Reservation, Service, Barber, Testimonial, HaircutStyle
import datetime
import random
import string


def _generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def book_reservation(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to book an appointment.')
            return redirect(f'/accounts/login/?next=/reservations/book/')

        barber_id        = request.POST.get('barber', '').strip()
        haircut_style_id = request.POST.get('haircut_style', '').strip()
        service_id       = request.POST.get('service', '').strip()
        appointment_date = request.POST.get('appointment_date', '').strip()
        appointment_time = request.POST.get('appointment_time', '').strip()
        notes            = request.POST.get('notes', '').strip()

        errors        = []
        barber        = None
        haircut_style = None
        service       = None

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

        if service_id:
            try:
                service = Service.objects(id=service_id).first()
            except Exception:
                service = None

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
            styles   = HaircutStyle.objects(is_active=True).order_by('category', 'price')
            barbers  = Barber.objects(is_active=True)
            services = Service.objects(is_active=True).order_by('category', 'price')
            return render(request, 'reservations/book.html', {
                'styles': styles, 'barbers': barbers, 'services': services,
            })

        total_price = 0
        if haircut_style and haircut_style.price is not None:
            total_price = haircut_style.price
        elif service and service.price is not None:
            total_price = service.price

        code = _generate_code()
        for _ in range(5):
            if not Reservation.objects(confirmation_code=code).first():
                break
            code = _generate_code()

        reservation = Reservation(
            customer_id=request.user.pk or 0,
            customer_username=request.user.username,
            customer_name=request.user.get_full_name() or request.user.username,
            barber=barber,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            total_price=total_price,
            confirmation_code=code,
        )

        try:
            reservation.save()
        except Exception as e:
            messages.error(request, f'Could not save reservation. Please try again. ({e})')
            styles   = HaircutStyle.objects(is_active=True).order_by('category', 'price')
            barbers  = Barber.objects(is_active=True)
            services = Service.objects(is_active=True).order_by('category', 'price')
            return render(request, 'reservations/book.html', {
                'styles': styles, 'barbers': barbers, 'services': services,
            })

        messages.success(
            request,
            f'Reservation confirmed! Your booking code is: {reservation.confirmation_code}'
        )
        return redirect('reservation_detail', pk=str(reservation.pk))

    styles   = HaircutStyle.objects(is_active=True).order_by('category', 'price')
    barbers  = Barber.objects(is_active=True)
    services = Service.objects(is_active=True).order_by('category', 'price')
    return render(request, 'reservations/book.html', {
        'styles': styles, 'barbers': barbers, 'services': services,
    })


@login_required
def my_reservations(request):
    try:
        reservations = Reservation.objects(
            customer_username=request.user.username
        ).order_by('-created_at')
        if reservations.count() == 0:
            reservations = Reservation.objects(
                customer_id=request.user.pk
            ).order_by('-created_at')
    except Exception:
        reservations = []
    return render(request, 'reservations/my_reservations.html', {
        'reservations': reservations,
    })


@login_required
def reservation_detail(request, pk):
    try:
        reservation = Reservation.objects(id=pk).first()
    except Exception:
        reservation = None

    if not reservation:
        messages.error(request, 'Reservation not found.')
        return redirect('my_reservations')

    if not request.user.is_staff:
        is_owner = (
            reservation.customer_username == request.user.username
            or reservation.customer_id == request.user.pk
        )
        if not is_owner:
            messages.error(request, 'Reservation not found.')
            return redirect('my_reservations')

    return render(request, 'reservations/detail.html', {'reservation': reservation})


@login_required
def cancel_reservation(request, pk):
    try:
        reservation = Reservation.objects(id=pk).first()
    except Exception:
        reservation = None

    if not reservation:
        messages.error(request, 'Reservation not found.')
        return redirect('my_reservations')

    if not request.user.is_staff:
        is_owner = (
            reservation.customer_username == request.user.username
            or reservation.customer_id == request.user.pk
        )
        if not is_owner:
            messages.error(request, 'Reservation not found.')
            return redirect('my_reservations')

    if reservation.status in ['pending', 'confirmed']:
        try:
            date_obj = datetime.date.fromisoformat(reservation.appointment_date)
            if date_obj >= timezone.now().date():
                reservation.status = 'cancelled'
                reservation.save()
                messages.success(request, 'Reservation cancelled successfully.')
            else:
                messages.error(request, 'Cannot cancel past reservations.')
        except Exception as e:
            messages.error(request, f'Could not cancel reservation. ({e})')
    else:
        messages.error(request, 'This reservation cannot be cancelled.')

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
        booked_times = set(
            r.appointment_time for r in Reservation.objects(
                barber=barber,
                appointment_date=date_str,
                status__in=['pending', 'confirmed'],
            )
        )
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
        rating         = request.POST.get('rating', 5)
        comment        = request.POST.get('comment', '').strip()
        reservation_id = request.POST.get('reservation_id', '').strip()
        service        = None

        if reservation_id:
            try:
                linked = Reservation.objects(id=reservation_id).first()
                if linked and linked.service:
                    service = linked.service
            except Exception:
                pass

        if not comment:
            messages.error(request, 'Please write a comment before submitting.')
            return redirect('user_dashboard')

        already = Testimonial.objects(
            customer_username=request.user.username,
            reservation_id=reservation_id,
        ).first() if reservation_id else None

        if already:
            messages.warning(request, 'You have already submitted a review for this appointment.')
            return redirect('user_dashboard')

        testimonial = Testimonial(
            customer_id=request.user.pk or 0,
            customer_username=request.user.username,
            customer_name=request.user.get_full_name() or request.user.username,
            reservation_id=reservation_id,
            rating=int(rating),
            comment=comment,
            service=service,
        )
        try:
            testimonial.save()
            messages.success(request, 'Thank you for your review! It will appear once approved.')
        except Exception as e:
            messages.error(request, f'Could not submit review. ({e})')
    return redirect('user_dashboard')


@login_required
def review_page(request):
    if request.method == 'POST':
        rating         = request.POST.get('rating', 5)
        comment        = request.POST.get('comment', '').strip()
        reservation_id = request.POST.get('reservation_id', '').strip()
        service        = None

        if reservation_id:
            try:
                linked = Reservation.objects(id=reservation_id).first()
                if linked and linked.service:
                    service = linked.service
            except Exception:
                pass

        if not comment:
            messages.error(request, 'Please write a comment before submitting.')
            my_reservations = Reservation.objects(
                customer_username=request.user.username,
                status='completed',
            ).order_by('-appointment_date')
            return render(request, 'reservations/review.html', {
                'my_reservations': my_reservations,
            })

        already = Testimonial.objects(
            customer_username=request.user.username,
            reservation_id=reservation_id,
        ).first() if reservation_id else None

        if already:
            messages.warning(request, 'You have already submitted a review for this appointment.')
            return redirect('review_page')

        try:
            rating_int = int(rating)
        except (ValueError, TypeError):
            rating_int = 5

        testimonial = Testimonial(
            customer_id=request.user.pk or 0,
            customer_username=request.user.username,
            customer_name=request.user.get_full_name() or request.user.username,
            reservation_id=reservation_id,
            rating=rating_int,
            comment=comment,
            service=service,
        )
        try:
            testimonial.save()
            messages.success(request, 'Thank you for your review! It will appear once approved.')
        except Exception as e:
            messages.error(request, f'Could not submit review. ({e})')
        return redirect('review_page')

    my_reservations = Reservation.objects(
        customer_username=request.user.username,
        status='completed',
    ).order_by('-appointment_date')
    my_testimonials = Testimonial.objects(
        customer_username=request.user.username,
    ).order_by('-created_at')
    return render(request, 'reservations/review.html', {
        'my_reservations': my_reservations,
        'my_testimonials': my_testimonials,
    })