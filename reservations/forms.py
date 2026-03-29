from django import forms
from django.utils import timezone
from .models import Service, Barber, HaircutStyle
import datetime


class ReservationForm(forms.Form):
    barber = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    service = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': str(timezone.now().date() + datetime.timedelta(days=1))
        })
    )
    appointment_time = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requests or notes...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['barber'].choices = [('', 'Select a barber...')] + [
            (str(b.id), f"{b.name} — {b.specialty}")
            for b in Barber.objects(is_active=True)
        ]
        self.fields['service'].choices = [('', 'Select a service...')] + [
            (str(s.id), f"{s.name} — ₱{s.price} ({s.duration_minutes} min)")
            for s in Service.objects(is_active=True)
        ]

        time_choices = [('', 'Select time')]
        for hour in range(8, 20):
            for minute in [0, 30]:
                t = datetime.time(hour, minute)
                time_choices.append((t.strftime('%H:%M'), t.strftime('%I:%M %p')))
        self.fields['appointment_time'].choices = time_choices

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date <= timezone.now().date():
            raise forms.ValidationError('Please select a future date.')
        return date

PRICE_TIER_CHOICES = (
    ('basic',    '₱70–₱100 · Traditional, basic cut'),
    ('finish',   '₱100–₱200 · Cleaner finish'),
    ('styled',   '₱200–₱350 · Styled cuts'),
    ('fade',     '₱350–₱600 · Advanced fades & shaping'),
    ('premium',  '₱600–₱1,000+ · Premium full service'),
)


class HaircutStyleForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Classic Buzz Cut',
        })
    )
    category = forms.ChoiceField(
        choices=PRICE_TIER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control form-control-tier'}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Brief description of this style...',
        })
    )
    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00',
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-file',
            'accept': 'image/jpeg,image/png,image/webp',
        })
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class TestimonialForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                     'placeholder': 'Share your experience...'})
    )
    service = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].choices = [('', '— Select service —')] + [
            (str(s.id), s.name) for s in Service.objects(is_active=True)
        ]