from django import forms
from django.utils import timezone
from .models import Reservation, Service, Barber, Testimonial, HaircutStyle
import datetime


class ReservationForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': str(timezone.now().date() + datetime.timedelta(days=1))
        })
    )
    appointment_time = forms.TimeField(
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                     'placeholder': 'Any special requests or notes...'})
    )

    class Meta:
        model = Reservation
        fields = ['barber', 'service', 'appointment_date', 'appointment_time', 'notes']
        widgets = {
            'barber': forms.Select(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barber'].queryset = Barber.objects.filter(is_active=True)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)

        time_choices = []
        for hour in range(8, 20):
            for minute in [0, 30]:
                t = datetime.time(hour, minute)
                time_choices.append((t.strftime('%H:%M'), t.strftime('%I:%M %p')))
        self.fields['appointment_time'].widget.choices = [('', 'Select time')] + time_choices

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date <= timezone.now().date():
            raise forms.ValidationError('Please select a future date.')
        return date

    def clean(self):
        cleaned_data = super().clean()
        barber = cleaned_data.get('barber')
        date = cleaned_data.get('appointment_date')
        time = cleaned_data.get('appointment_time')
        if barber and date and time:
            existing = Reservation.objects.filter(
                barber=barber,
                appointment_date=date,
                appointment_time=time,
                status__in=['pending', 'confirmed']
            )
            if existing.exists():
                raise forms.ValidationError('This time slot is already booked. Please choose another.')
        return cleaned_data


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['rating', 'comment', 'service']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                             'placeholder': 'Share your experience...'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
        }


class HaircutStyleForm(forms.ModelForm):
    class Meta:
        model = HaircutStyle
        fields = ['name', 'category', 'description', 'price', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Classic Buzz Cut'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                 'placeholder': 'Brief description of this style...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01',
                                              'placeholder': '0.00'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
