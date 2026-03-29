import secrets
import string
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reservations.models import Service, Barber, Testimonial, HaircutStyle
from accounts.models import UserProfile
from decimal import Decimal


def _generate_password(length=16):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class Command(BaseCommand):
    help = 'Seeds the database with sample data for Velvet Steel Barbershop'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Velvet Steel Barbershop data...')

        # ── SERVICES ────────────────────────────────────────────
        # Pricing tiers:
        #   ₱70–₱100   Traditional, basic cut
        #   ₱100–₱200  Cleaner finish, more attention to detail
        #   ₱200–₱350  Styled cuts, better tools, consistent results
        #   ₱350–₱600  Advanced fades, shaping, optional wash/styling
        #   ₱600–₱1000+ Premium experience, precision work, full service
        services_data = [
            {
                'name': 'Youth Cut',
                'category': 'kids',
                'description': 'Clean, comfortable haircut for boys 12 and under. Patient service, no rushing. Includes a wash and simple style.',
                'price': Decimal('85'),
                'duration_minutes': 30,
                'icon': 'child',
            },
            {
                'name': 'Classic Haircut',
                'category': 'haircut',
                'description': 'Traditional Filipino barbershop cut — scissors and clipper work, clean neckline, no extras. Reliable and precise.',
                'price': Decimal('150'),
                'duration_minutes': 30,
                'icon': 'cut',
            },
            {
                'name': 'Textured Crop',
                'category': 'haircut',
                'description': 'Modern disconnected crop with texture. Consultation-driven cut tailored to your hair type. Includes wash, cut, and texture paste finish.',
                'price': Decimal('280'),
                'duration_minutes': 45,
                'icon': 'cut',
            },
            {
                'name': 'Beard Sculpture',
                'category': 'shave',
                'description': 'Full beard shaping with straight razor edge, beard oil treatment, and styling. Clean lines, defined shape.',
                'price': Decimal('380'),
                'duration_minutes': 30,
                'icon': 'user-tie',
            },
            {
                'name': 'Scalp and Hair Treatment',
                'category': 'treatment',
                'description': 'Deep-conditioning scalp treatment with hot oil massage, protein mask, and a cooling scalp rinse. Leaves hair healthy and revived.',
                'price': Decimal('480'),
                'duration_minutes': 60,
                'icon': 'spa',
            },
            {
                'name': 'Classic Straight Razor Shave',
                'category': 'shave',
                'description': 'Full hot-towel prep, pre-shave oil, premium lather, straight razor shave, cold towel close, and aftershave balm. A complete ritual.',
                'price': Decimal('520'),
                'duration_minutes': 45,
                'icon': 'user-tie',
            },
            {
                'name': 'Fade and Wash',
                'category': 'combo',
                'description': 'Precision fade with a full shampoo and conditioning wash, blowdry, and styled finish. Clean from root to neckline.',
                'price': Decimal('550'),
                'duration_minutes': 60,
                'icon': 'cut',
            },
            {
                'name': 'Signature Haircut',
                'category': 'haircut',
                'description': 'Our house cut — precision scissor work with a tailored consultation, hot towel neck finish, and blowout styling. Built for the modern Filipino professional.',
                'price': Decimal('650'),
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
                'name': 'Gentleman Package',
                'category': 'combo',
                'description': 'Precision fade plus beard sculpture plus scalp treatment. No filler, no rush. The complete mid-week reset.',
                'price': Decimal('900'),
                'duration_minutes': 90,
                'icon': 'star',
            },
            {
                'name': 'Velvet Steel Complete',
                'category': 'combo',
                'description': 'Our flagship experience. Signature haircut, straight razor shave, beard sculpt, full scalp treatment, and hot towel finish. End-to-end grooming for the discerning gentleman.',
                'price': Decimal('1500'),
                'duration_minutes': 120,
                'icon': 'crown',
            },
        ]

        created_services = 0
        for sdata in services_data:
            obj, created = Service.objects.get_or_create(name=sdata['name'], defaults=sdata)
            if created:
                created_services += 1
        self.stdout.write(f'  {created_services} services created')

        # ── BARBERS ─────────────────────────────────────────────
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

        # ── ADMIN USER ──────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin_password = os.environ.get('ADMIN_SEED_PASSWORD') or _generate_password()
            admin = User.objects.create_superuser('admin', 'admin@velvetsteel.ph', admin_password)
            UserProfile.objects.create(user=admin, phone='+639123456789', city='Quezon City')
            self.stdout.write(self.style.WARNING(
                f'  Admin user created — username: admin / password: {admin_password}'
            ))
            self.stdout.write(self.style.WARNING(
                '  SAVE THIS PASSWORD NOW. It will not be shown again.'
            ))
        else:
            self.stdout.write('  Admin user already exists')

        # ── TESTIMONIALS ─────────────────────────────────────────
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

        # ── HAIRCUT STYLES ───────────────────────────────────────
        # 10 categories × styles. Images are uploaded via the admin panel.
        # Prices follow the tier guide in the services section above.
        styles_data = [
            # Buzz Cut
            {'category': 'buzz_cut', 'name': 'Classic Buzz Cut', 'price': Decimal('85'), 'description': 'Clean all-over clipper cut at a single guard length. No frills, no fade — just precision.'},
            {'category': 'buzz_cut', 'name': 'High & Tight Buzz', 'price': Decimal('100'), 'description': 'Very short on the sides and back, slightly longer on top. Military-inspired, always sharp.'},
            {'category': 'buzz_cut', 'name': 'Induction Cut', 'price': Decimal('75'), 'description': 'The shortest buzz possible — near-zero guard. Low maintenance, maximum clean.'},
            {'category': 'buzz_cut', 'name': 'Faded Buzz Cut', 'price': Decimal('150'), 'description': 'Buzz on top with a tapered or faded sides for a more polished, structured look.'},
            {'category': 'buzz_cut', 'name': 'Butch Cut', 'price': Decimal('90'), 'description': 'Slightly longer than a standard buzz with a natural fade at the sides. Comfortable and clean.'},

            # Modern Mullet
            {'category': 'modern_mullet', 'name': 'Business Mullet', 'price': Decimal('280'), 'description': 'Styled short on top, tapered sides, longer at the nape. Professional up front, personality in the back.'},
            {'category': 'modern_mullet', 'name': 'Curly Mullet', 'price': Decimal('300'), 'description': 'Takes advantage of natural curl or texture — cropped front and sides, full and voluminous at the back.'},
            {'category': 'modern_mullet', 'name': 'Undercut Mullet', 'price': Decimal('320'), 'description': 'Shaved undercut sides with length kept at the nape. Edgy, deliberate, and very on-trend.'},
            {'category': 'modern_mullet', 'name': 'Shag Mullet', 'price': Decimal('350'), 'description': 'Layered, textured mullet with a relaxed finish. Works on wavy or straight hair.'},
            {'category': 'modern_mullet', 'name': 'Rat Tail Mullet', 'price': Decimal('280'), 'description': 'Short all around with a single defined strand left long at the nape. Bold statement cut.'},

            # Burst Fade
            {'category': 'burst_fade', 'name': 'Low Burst Fade', 'price': Decimal('380'), 'description': 'A semi-circular fade around the ear that blends into longer hair on top. Clean and versatile.'},
            {'category': 'burst_fade', 'name': 'Mid Burst Fade', 'price': Decimal('420'), 'description': 'Fade starting at mid-ear level, radiating outward for a bold arc effect with great contrast.'},
            {'category': 'burst_fade', 'name': 'High Burst Fade', 'price': Decimal('450'), 'description': 'Dramatic burst fade starting high up on the sides, maximizing contrast and shape.'},
            {'category': 'burst_fade', 'name': 'Afro Burst Fade', 'price': Decimal('500'), 'description': 'Burst fade designed to frame and enhance natural afro or curly hair texture with a rounded silhouette.'},
            {'category': 'burst_fade', 'name': 'Mohawk Burst Fade', 'price': Decimal('480'), 'description': 'Burst fade on the sides with a defined strip of longer hair on top — structured and clean.'},

            # Curtain Bangs
            {'category': 'curtain_bangs', 'name': 'Classic Curtains', 'price': Decimal('200'), 'description': 'Center-parted hair that frames the face on both sides. Timeless and effortlessly cool.'},
            {'category': 'curtain_bangs', 'name': 'Wavy Curtain Bangs', 'price': Decimal('220'), 'description': 'Curtain cut styled to emphasize natural wave. Adds flow and movement to the overall look.'},
            {'category': 'curtain_bangs', 'name': 'Long Curtain Cut', 'price': Decimal('250'), 'description': 'Extended length curtains falling past the ears. Relaxed, slightly bohemian with structure.'},
            {'category': 'curtain_bangs', 'name': 'Textured Curtains', 'price': Decimal('280'), 'description': 'Center-parted with point-cut ends and added texture for a modern, deconstructed finish.'},
            {'category': 'curtain_bangs', 'name': 'Curtain Fade', 'price': Decimal('350'), 'description': 'Classic curtain top paired with a taper or fade on the sides for a cleaner, more structured shape.'},

            # Skin Fade
            {'category': 'skin_fade', 'name': 'Low Skin Fade', 'price': Decimal('400'), 'description': 'Skin fade starting just above the ear, blending seamlessly into the natural hair above.'},
            {'category': 'skin_fade', 'name': 'Mid Skin Fade', 'price': Decimal('450'), 'description': 'Starts at mid-temple — the most popular fade position. Balanced contrast and clean transition.'},
            {'category': 'skin_fade', 'name': 'High Skin Fade', 'price': Decimal('480'), 'description': 'Fade starts high on the head, maximizing contrast between bare skin and hair on top.'},
            {'category': 'skin_fade', 'name': 'Temp Fade', 'price': Decimal('520'), 'description': 'Also called a temple fade — fade concentrated at the temples for a sharp, defined frame.'},
            {'category': 'skin_fade', 'name': 'Drop Skin Fade', 'price': Decimal('500'), 'description': 'The fade line drops behind the ear in a curved arc for a distinctive, premium look.'},

            # Undercut
            {'category': 'undercut', 'name': 'Classic Undercut', 'price': Decimal('350'), 'description': 'All sides shaved or clipped short with longer hair on top. Clean disconnection, strong contrast.'},
            {'category': 'undercut', 'name': 'Disconnected Undercut', 'price': Decimal('400'), 'description': 'Extreme contrast between shaved sides and longer top — no blending, very deliberate.'},
            {'category': 'undercut', 'name': 'Slicked Undercut', 'price': Decimal('420'), 'description': 'Undercut with the top styled back with pomade. Sharp, refined, and commanding.'},
            {'category': 'undercut', 'name': 'Long Top Undercut', 'price': Decimal('380'), 'description': 'Keeps the top at shoulder-adjacent length, tucked or flowing freely. Versatile and expressive.'},
            {'category': 'undercut', 'name': 'Undercut Pompadour', 'price': Decimal('450'), 'description': 'Undercut sides with a voluminous swept-back top. Bold, classic, and unmistakable.'},

            # Textured Crop
            {'category': 'textured_crop', 'name': 'French Crop', 'price': Decimal('180'), 'description': 'Short fringe cut straight across with textured sides. Clean, minimal, and always in style.'},
            {'category': 'textured_crop', 'name': 'Textured Quiff Crop', 'price': Decimal('250'), 'description': 'Short crop with a lifted, textured front. Product-friendly and works great on thicker hair.'},
            {'category': 'textured_crop', 'name': 'Drop Fade Crop', 'price': Decimal('320'), 'description': 'Textured crop paired with a drop fade on the sides. Structured up top, clean down the sides.'},
            {'category': 'textured_crop', 'name': 'Blunt Crop', 'price': Decimal('180'), 'description': 'Heavy, blunt fringe with clipped sides. Bold and graphic — no apologies.'},
            {'category': 'textured_crop', 'name': 'Skin Fade Crop', 'price': Decimal('350'), 'description': 'Textured crop on top with a clean skin fade. One of the most requested cuts at the shop.'},

            # Pompadour
            {'category': 'pompadour', 'name': 'Classic Pompadour', 'price': Decimal('450'), 'description': 'Voluminous top swept back and upward. Side-swept, structured, and unmistakably bold.'},
            {'category': 'pompadour', 'name': 'Modern Pompadour', 'price': Decimal('480'), 'description': 'Pompadour with a lower, more relaxed volume. Contemporary fit for daily wear.'},
            {'category': 'pompadour', 'name': 'Fade Pompadour', 'price': Decimal('520'), 'description': 'High-volume pomp paired with a skin or taper fade on the sides. Maximum contrast.'},
            {'category': 'pompadour', 'name': 'Disconnected Pompadour', 'price': Decimal('550'), 'description': 'Sharp, shaved sides with no blend into the voluminous top. Striking and precise.'},
            {'category': 'pompadour', 'name': 'Textured Pompadour', 'price': Decimal('480'), 'description': 'Pompadour with a piece-y, textured finish rather than a hard, lacquered look. More wearable.'},

            # Quiff
            {'category': 'quiff', 'name': 'Classic Quiff', 'price': Decimal('350'), 'description': 'Hair lifted and swept forward at the front with a tapered finish on the sides. Clean volume.'},
            {'category': 'quiff', 'name': 'Modern Quiff', 'price': Decimal('380'), 'description': 'Shorter, more relaxed quiff with a skin or drop fade on the sides for a contemporary feel.'},
            {'category': 'quiff', 'name': 'Disconnected Quiff', 'price': Decimal('420'), 'description': 'Quiff with a shaved side — strong disconnection between the styled top and the bare skin.'},
            {'category': 'quiff', 'name': 'Textured Quiff', 'price': Decimal('400'), 'description': 'Piece-y, matte-finish quiff. Works especially well on naturally thick or coarse hair.'},
            {'category': 'quiff', 'name': 'Long Quiff', 'price': Decimal('430'), 'description': 'Extended quiff length swept back or to the side. More dramatic, fashion-forward take.'},

            # French Crop
            {'category': 'french_crop', 'name': 'Standard French Crop', 'price': Decimal('180'), 'description': 'Clean fringe cut bluntly across the forehead with short sides. Simple, low-maintenance, sharp.'},
            {'category': 'french_crop', 'name': 'Fade French Crop', 'price': Decimal('280'), 'description': 'French crop on top with a taper or skin fade on the sides. The most popular variant.'},
            {'category': 'french_crop', 'name': 'Textured French Crop', 'price': Decimal('250'), 'description': 'French crop with a choppy, textured fringe rather than a blunt cut. More dynamic and modern.'},
            {'category': 'french_crop', 'name': 'Fringe Crop', 'price': Decimal('200'), 'description': 'Slightly longer fringe that falls forward. Softer take on the French crop for a more casual vibe.'},
            {'category': 'french_crop', 'name': 'High Fade French Crop', 'price': Decimal('320'), 'description': 'Clean French crop paired with a high fade for a bold, well-defined silhouette.'},
        ]

        created_styles = 0
        for sdata in styles_data:
            obj, created = HaircutStyle.objects.get_or_create(
                name=sdata['name'], category=sdata['category'], defaults=sdata
            )
            if created:
                created_styles += 1
        self.stdout.write(f'  {created_styles} haircut styles created')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))
        self.stdout.write('')
        self.stdout.write('Admin panel:  /admin-panel/')
        self.stdout.write('Django admin: /django-admin/')
