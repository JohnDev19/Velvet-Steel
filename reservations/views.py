from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Reservation, Service, Barber, Testimonial
from .forms import ReservationForm, TestimonialForm
import datetime


@login_required
def book_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.customer = request.user
            reservation.total_price = reservation.service.price
            reservation.save()
            messages.success(request, f'Reservation confirmed! Your code: {reservation.confirmation_code}')
            return redirect('reservation_detail', pk=reservation.pk)
    else:
        form = ReservationForm()
    services = Service.objects.filter(is_active=True)
    barbers = Barber.objects.filter(is_active=True)
    return render(request, 'reservations/book.html', {
        'form': form, 'services': services, 'barbers': barbers
    })


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'reservations/my_reservations.html', {'reservations': reservations})


@login_required
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    return render(request, 'reservations/detail.html', {'reservation': reservation})


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, customer=request.user)
    if reservation.status in ['pending', 'confirmed']:
        if reservation.appointment_date > timezone.now().date():
            reservation.status = 'cancelled'
            reservation.save()
            messages.success(request, 'Reservation cancelled successfully.')
        else:
            messages.error(request, 'Cannot cancel past reservations.')
    return redirect('my_reservations')


def get_available_slots(request):
    barber_id = request.GET.get('barber_id')
    date_str = request.GET.get('date')
    if not barber_id or not date_str:
        return JsonResponse({'slots': []})
    try:
        barber = Barber.objects.get(pk=barber_id)
        date = datetime.date.fromisoformat(date_str)
    except (Barber.DoesNotExist, ValueError):
        return JsonResponse({'slots': []})

    booked_times = Reservation.objects.filter(
        barber=barber, appointment_date=date,
        status__in=['pending', 'confirmed']
    ).values_list('appointment_time', flat=True)

    all_slots = []
    for hour in range(8, 20):
        for minute in [0, 30]:
            t = datetime.time(hour, minute)
            if t not in booked_times:
                all_slots.append({
                    'value': t.strftime('%H:%M'),
                    'label': t.strftime('%I:%M %p')
                })
    return JsonResponse({'slots': all_slots})


@login_required
def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.customer = request.user
            testimonial.customer_name = request.user.get_full_name() or request.user.username
            testimonial.save()
            messages.success(request, 'Thank you for your review! It will appear once approved.')
            return redirect('home')
    return redirect('home')
