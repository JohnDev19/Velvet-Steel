from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reservations.models import Service, Barber, Testimonial
from accounts.models import UserProfile
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds the database with sample data for Velvet Steel Barbershop'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Velvet Steel Barbershop data...')

        services_data = [
            {
                'name': 'Signature Haircut',
                'category': 'haircut',
                'description': 'Our house cut — precision scissor work with a tailored consultation, hot towel neck finish, and blowout styling. Built for the modern Filipino professional.',
                'price': Decimal('600'),
                'duration_minutes': 45,
                'icon': 'cut',
            },
            {
                'name': 'Precision Fade',
                'category': 'haircut',
                'description': 'Skin-to-full fade with razor-sharp lines. Includes a detailed temple and neckline cleanup and a styled finish with premium pomade.',
                'price': Decimal('750'),
                'duration_minutes': 60,
                'icon': 'cut',
            },
            {
                'name': 'Textured Crop',
                'category': 'haircut',
                'description': 'Modern disconnected crop with texture. Consultation-driven cut tailored to your hair type. Wash, cut, texture paste finish.',
                'price': Decimal('700'),
                'duration_minutes': 50,
                'icon': 'cut',
            },
            {
                'name': 'Classic Straight Razor Shave',
                'category': 'shave',
                'description': 'Full hot-towel prep, pre-shave oil, premium lather, straight razor shave, cold towel close, and aftershave balm. A complete ritual.',
                'price': Decimal('650'),
                'duration_minutes': 45,
                'icon': 'user-tie',
            },
            {
                'name': 'Beard Sculpture',
                'category': 'shave',
                'description': 'Full beard shaping with straight razor edge, beard oil treatment, and styling. Clean lines, defined shape.',
                'price': Decimal('500'),
                'duration_minutes': 30,
                'icon': 'user-tie',
            },
            {
                'name': 'Scalp and Hair Treatment',
                'category': 'treatment',
                'description': 'Deep-conditioning scalp treatment with hot oil massage, protein mask, and a cooling scalp rinse. Leaves hair healthy and revived.',
                'price': Decimal('800'),
                'duration_minutes': 60,
                'icon': 'spa',
            },
            {
                'name': 'Velvet Steel Complete',
                'category': 'combo',
                'description': 'Our flagship experience. Signature haircut, straight razor shave, beard sculpt, full scalp treatment, and hot towel finish. End-to-end grooming for the discerning gentleman.',
                'price': Decimal('1800'),
                'duration_minutes': 120,
                'icon': 'crown',
            },
            {
                'name': 'Gentleman Package',
                'category': 'combo',
                'description': 'Precision fade plus beard sculpture plus scalp treatment. No filler, no rush. The complete mid-week reset.',
                'price': Decimal('1200'),
                'duration_minutes': 90,
                'icon': 'star',
            },
            {
                'name': 'Fade and Wash',
                'category': 'combo',
                'description': 'Precision fade with a full shampoo and conditioning wash, blowdry, and styled finish. Clean from root to neckline.',
                'price': Decimal('850'),
                'duration_minutes': 60,
                'icon': 'cut',
            },
            {
                'name': 'Youth Cut',
                'category': 'kids',
                'description': 'Clean, comfortable haircut for boys 12 and under. Patient service, no rushing. Includes a wash and simple style.',
                'price': Decimal('500'),
                'duration_minutes': 30,
                'icon': 'child',
            },
        ]

        created_services = 0
        for sdata in services_data:
            obj, created = Service.objects.get_or_create(name=sdata['name'], defaults=sdata)
            if created:
                created_services += 1
        self.stdout.write(f'  {created_services} services created')

        barbers_data = [
            {
                'name': 'Rico Villanueva',
                'specialty': 'Straight Razor Shaves, Classic Cuts and Fades',
                'bio': 'Founder of Velvet Steel. Trained in Manila and refined in Barcelona, Rico brings fifteen years of old-world barbering precision to every service. His straight razor work is unmatched in Metro Manila.',
                'experience_years': 15,
                'rating': Decimal('5.0'),
                'instagram': '@velvetsteel_ph',
            },
            {
                'name': 'Marco dela Cruz',
                'specialty': 'Skin Fades, Beard Sculpting and Design Lines',
                'bio': 'Marco is the most-requested barber at Velvet Steel. Known for razor-clean fades and obsessive attention to symmetry, he has built a loyal clientele across QC in eight years of professional work.',
                'experience_years': 8,
                'rating': Decimal('4.9'),
                'instagram': '@marco.cuts',
            },
            {
                'name': 'Jonas Reyes',
                'specialty': 'Textured Crops, Modern Styling and Hair Art',
                'bio': 'The creative director of Velvet Steel cuts. Jonas specializes in contemporary Filipino streetwear-influenced styles including textured crops, disconnected fades, and design lines.',
                'experience_years': 6,
                'rating': Decimal('4.9'),
                'instagram': '@jonasreyes.cuts',
            },
            {
                'name': 'Donna Santos',
                'specialty': 'Youth Cuts, Family Grooming and Scalp Treatments',
                'bio': 'Donna is the most patient and precise technician on the floor. She specializes in youth cuts and scalp health treatments, making every client feel completely at ease.',
                'experience_years': 5,
                'rating': Decimal('5.0'),
                'instagram': '@donnasantos.cuts',
            },
        ]

        created_barbers = 0
        for bdata in barbers_data:
            obj, created = Barber.objects.get_or_create(name=bdata['name'], defaults=bdata)
            if created:
                created_barbers += 1
        self.stdout.write(f'  {created_barbers} barbers created')

        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@velvetsteel.ph', 'admin123')
            UserProfile.objects.create(user=admin, phone='+63 912 345 6789', city='Quezon City')
            self.stdout.write('  Admin user created  username: admin / password: admin123')
        else:
            self.stdout.write('  Admin user already exists')

        if not User.objects.filter(username='juandc').exists():
            customer = User.objects.create_user(
                'juandc', 'juan@email.com', 'password123',
                first_name='Juan', last_name='dela Cruz'
            )
            UserProfile.objects.create(user=customer, phone='+63 917 111 2222', city='Quezon City')
            self.stdout.write('  Test customer created  username: juandc / password: password123')

        testimonials_data = [
            {
                'customer_name': 'Juan dela Cruz',
                'rating': 5,
                'comment': 'Best barbershop experience I have had in Manila. Rico knows exactly what he is doing — clean fade, precise lines, and the straight razor shave is on another level. Worth every peso.',
                'is_approved': True,
            },
            {
                'customer_name': 'Miguel Santos',
                'rating': 5,
                'comment': 'The Velvet Steel Complete package is absolutely worth it. Two hours of full grooming and I walked out looking sharp. The hot towel ritual alone justifies the price.',
                'is_approved': True,
            },
            {
                'customer_name': 'Ramon Reyes',
                'rating': 5,
                'comment': 'Online booking is seamless. No waiting, no confusion. Marco nailed the skin fade exactly as I described. This is what a premium barbershop should feel like.',
                'is_approved': True,
            },
            {
                'customer_name': 'Carlo Mendoza',
                'rating': 5,
                'comment': 'Clean shop, serious barbers, zero small talk unless you want it. Jonas gave me the best textured crop I have ever had. I do not go anywhere else now.',
                'is_approved': True,
            },
            {
                'customer_name': 'Ariel Bautista',
                'rating': 5,
                'comment': 'Took my son for a youth cut with Donna — she was incredibly patient and the result was perfect. He actually enjoyed the experience. We will be regulars.',
                'is_approved': True,
            },
        ]

        created_t = 0
        for tdata in testimonials_data:
            obj, created = Testimonial.objects.get_or_create(
                customer_name=tdata['customer_name'], defaults=tdata
            )
            if created:
                created_t += 1
        self.stdout.write(f'  {created_t} testimonials created')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))
        self.stdout.write('')
        self.stdout.write('Admin panel:  http://127.0.0.1:8000/admin-panel/')
        self.stdout.write('Django admin: http://127.0.0.1:8000/django-admin/')
        self.stdout.write('Credentials:  admin / admin123')
