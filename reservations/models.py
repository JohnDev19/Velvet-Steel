from mongoengine import (
    Document,
    StringField, IntField, DecimalField, BooleanField,
    DateTimeField,
    ReferenceField,
    CASCADE,
)
from django.utils import timezone
import datetime
import random
import string


class Service(Document):
    CATEGORY_CHOICES = (
        ('haircut', 'Haircut'),
        ('shave', 'Shave & Beard'),
        ('treatment', 'Hair Treatment'),
        ('combo', 'Combo Package'),
        ('kids', "Kids' Cut"),
    )

    name = StringField(max_length=100, required=True)
    category = StringField(max_length=20, choices=CATEGORY_CHOICES, default='haircut')
    description = StringField()
    price = DecimalField(precision=2)
    duration_minutes = IntField(default=30)
    is_active = BooleanField(default=True)
    icon = StringField(max_length=50, default='scissors')
    image = StringField()
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_service',
        'ordering': ['category', 'price'],
    }

    def __str__(self):
        return f"{self.name} - ₱{self.price}"

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)


class Barber(Document):
    name = StringField(max_length=100, required=True)
    specialty = StringField(max_length=200)
    bio = StringField()
    experience_years = IntField(default=1)
    photo = StringField()
    is_active = BooleanField(default=True)
    rating = DecimalField(precision=1, default=5.0)
    instagram = StringField(max_length=100)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_barber',
        'ordering': ['name'],
    }

    def __str__(self):
        return self.name


class Reservation(Document):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    customer_id = IntField(required=True)
    customer_username = StringField(max_length=150)
    customer_name = StringField(max_length=200)

    barber = ReferenceField(Barber, reverse_delete_rule=CASCADE)
    service = ReferenceField(Service, reverse_delete_rule=CASCADE, null=True)

    appointment_date = StringField()   # stored as "YYYY-MM-DD" string
    appointment_time = StringField()   # stored as "HH:MM" string
    status = StringField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = StringField()
    total_price = DecimalField(precision=2)
    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)
    confirmation_code = StringField(max_length=10, unique=True)

    meta = {
        'collection': 'reservations_reservation',
        'ordering': ['-appointment_date', '-appointment_time'],
    }

    def __str__(self):
        return f"{self.customer_name} - {self.appointment_date} {self.appointment_time}"

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property
    def appointment_date_display(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%B %d, %Y')
        except Exception:
            return self.appointment_date or '—'

    @property
    def appointment_time_display(self):
        try:
            return datetime.time.fromisoformat(self.appointment_time).strftime('%I:%M %p')
        except Exception:
            return self.appointment_time or '—'

    @property
    def appointment_month(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%b')
        except Exception:
            return ''

    @property
    def appointment_day(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%d')
        except Exception:
            return ''

    @property
    def appointment_year(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date).strftime('%Y')
        except Exception:
            return ''

    @property
    def appointment_date_obj(self):
        try:
            return datetime.date.fromisoformat(self.appointment_date)
        except Exception:
            return None

    @property
    def appointment_time_obj(self):
        try:
            return datetime.time.fromisoformat(self.appointment_time)
        except Exception:
            return None

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            self.confirmation_code = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )
        if self.total_price is None:
            try:
                self.total_price = self.service.price if self.service else 0
            except Exception:
                self.total_price = 0
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class Testimonial(Document):
    customer_id = IntField(null=True)
    customer_username = StringField(max_length=150)
    customer_name = StringField(max_length=100)
    reservation_id = StringField(max_length=50)
    rating = IntField(min_value=1, max_value=5, default=5)
    comment = StringField()
    service = ReferenceField(Service, null=True)
    is_approved = BooleanField(default=False)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_testimonial',
        'ordering': ['-created_at'],
    }

    def __str__(self):
        return f"{self.customer_name} - {self.rating}★"


class GalleryImage(Document):
    title = StringField(max_length=100)
    image = StringField()
    barber = ReferenceField(Barber, null=True)
    is_featured = BooleanField(default=False)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_galleryimage',
        'ordering': ['-created_at'],
    }

    def __str__(self):
        return self.title

class AboutPage(Document):
    page_badge       = StringField(default='OUR STORY')
    page_hero_title  = StringField(default='About <em>Velvet Steel</em>')
    page_hero_subtitle = StringField(default='Fifteen years of craftsmanship, passion, and Filipino pride')
    
    # Shop image
    shop_image       = StringField()

    # Hero / badge
    established_year = StringField(default='2010')

    # Stats row
    stat_years       = StringField(default='15+')
    stat_clients     = StringField(default='5K+')
    stat_barbers     = StringField(default='8+')

    # Story text
    story_section_title  = StringField(default='The <em>Legacy</em> of Velvet Steel')
    story_lead       = StringField(default='Founded in 2010 by master barber Rico Villanueva in the heart of Quezon City, Velvet Steel was built on a single conviction: that Filipino men deserve a genuinely premium grooming experience.')
    story_body_1     = StringField(default='What started as a small, humble shop on Rizal Avenue has grown into Metro Manila\'s most respected premium barbershop — a place where tradition meets modernity, and where every client is treated like royalty.')
    story_body_2     = StringField(default='We believe that a great haircut is more than just a trim — it\'s an expression of identity, a confidence booster, and a moment of self-care that every man deserves. That\'s why we pour passion, precision, and artistry into every single appointment.')

    # checklist
    value_1          = StringField(default='Certified Master Barbers')
    value_2          = StringField(default='Premium Imported Products')
    value_3          = StringField(default='Strict Hygiene Standards')
    value_4          = StringField(default='100% Filipino-Owned Business')

    # Contact
    address          = StringField(default='123 Rizal Avenue, Quezon City, Metro Manila, Philippines 1100')
    phone_1          = StringField(default='+63 912 345 6789')
    phone_2          = StringField(default='+63 2 8123 4567')
    email_1          = StringField(default='info@velvetsteel.ph')
    email_2          = StringField(default='bookings@velvetsteel.ph')
    hours_weekday    = StringField(default='Mon–Sat: 8:00 AM – 8:00 PM')
    hours_sunday     = StringField(default='Sunday: 9:00 AM – 6:00 PM')

    updated_at       = DateTimeField(default=timezone.now)

    meta = {'collection': 'about_page_content'}

    @classmethod
    def get_singleton(cls):
        obj = cls.objects().first()
        return obj  # None

class ServicesPage(Document):
    hero_subtitle        = StringField(default='Premium grooming crafted for the modern Filipino gentleman')
    section_badge        = StringField(default='GROOMING MENU')
    section_subtitle     = StringField(default='Every service follows our quality tiers — from traditional basics to full premium experiences.')
    cta_text             = StringField(default='Book your appointment now and let our masters work their magic.')
    updated_at           = DateTimeField(default=timezone.now)

    meta = {'collection': 'services_page_content'}

    @classmethod
    def get_singleton(cls):
        return cls.objects().first()

class HomePage(Document):
    # Hero
    hero_location        = StringField(default='QUEZON CITY — METRO MANILA')
    hero_small_title     = StringField(default='Precision. Craft.')
    hero_large_title     = StringField(default='Velvet Steel')
    hero_subtitle        = StringField(default='Premium barbershop grooming in the heart of Metro Manila. Old-world technique, uncompromising standards, modern sensibility.')

    # Features
    feat1_title          = StringField(default='Premium Standard')
    feat1_desc           = StringField(default='Every service uses imported professional-grade products. No shortcuts. No compromise on quality from the first cut to the last finish.')
    feat2_title          = StringField(default='Certified Barbers')
    feat2_desc           = StringField(default='Our team of master barbers has trained and refined their craft across Manila, Spain, and Japan. Technique is never left to chance.')
    feat3_title          = StringField(default='Online Booking')
    feat3_desc           = StringField(default='Reserve your exact slot in seconds. Real-time availability, instant confirmation, no phone calls required. Your time is valued.')
    feat4_title          = StringField(default='Strict Hygiene')
    feat4_desc           = StringField(default='Full tool sterilization between every client. A clean, orderly environment is not optional — it is the baseline at Velvet Steel.')

    # Section subtitles
    services_subtitle    = StringField(default='From signature fades to full grooming rituals. Every service is a deliberate act of craft, not a transaction.')
    barbers_subtitle     = StringField(default='Specialists, not generalists. Every barber at Velvet Steel has a defined craft and years of deliberate practice behind it.')
    testimonials_subtitle= StringField(default='Real words from real clients. Every review is a reflection of the craft, care, and consistency we bring to every cut.')

    # CTA banner
    cta_subtitle         = StringField(default='Reserve your slot online in seconds. Real-time availability, confirmed instantly. Walk in ready, walk out sharp.')
    cta_phone            = StringField(default='+639123456789')

    # Location section
    loc_address          = StringField(default='123 Rizal Avenue, Quezon City\nMetro Manila, Philippines')
    loc_hours_weekday    = StringField(default='Monday – Saturday: 8:00 AM – 8:00 PM')
    loc_hours_sunday     = StringField(default='Sunday: 9:00 AM – 6:00 PM')
    loc_phone            = StringField(default='+63 912 345 6789')
    loc_email            = StringField(default='info@velvetsteel.ph')
    loc_map_city         = StringField(default='Quezon City, Metro Manila')
    loc_map_country      = StringField(default='Philippines')
    loc_map_embed        = StringField(default='https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3860.819515648185!2d121.04945731484!3d14.647037989777!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3397b70c45a1e40f%3A0x9e4f61e1eb6cc49e!2sQuezon%20City%2C%20Metro%20Manila!5e0!3m2!1sen!2sph!4v1609459200000!5m2!1sen!2sph')

    updated_at           = DateTimeField(default=timezone.now)

    meta = {'collection': 'home_page_content'}

    @classmethod
    def get_singleton(cls):
        return cls.objects().first()
        
class HaircutStyle(Document):
    CATEGORY_CHOICES = (
        ('basic',   '₱70–₱100 · Traditional, basic cut'),
        ('finish',  '₱100–₱200 · Cleaner finish'),
        ('styled',  '₱200–₱350 · Styled cuts'),
        ('fade',    '₱350–₱600 · Advanced fades & shaping'),
        ('premium', '₱600–₱1,000+ · Premium full service'),
    )

    name = StringField(max_length=120, required=True)
    category = StringField(max_length=30, choices=CATEGORY_CHOICES)
    description = StringField()
    price = DecimalField(precision=2)
    image = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=timezone.now)

    meta = {
        'collection': 'reservations_haircutstyle',
        'ordering': ['category', 'price'],
    }

    def __str__(self):
        return f"{self.get_category_display()} – {self.name}"

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)


class SiteSettings(Document):
    # Identity
    shop_name        = StringField(default='Velvet Steel')
    shop_sub         = StringField(default='BARBERSHOP')
    shop_tagline     = StringField(default='Premium grooming. Deliberate craft.')
    shop_since       = StringField(default="Quezon City's finest since 2010.")

    # Footer contact block
    footer_address   = StringField(default='123 Rizal Avenue, Quezon City, Metro Manila')
    footer_phone     = StringField(default='+63 912 345 6789')
    footer_email     = StringField(default='info@velvetsteel.ph')
    footer_hours_wd  = StringField(default='Mon\u2013Sat: 8:00 AM \u2013 8:00 PM')
    footer_hours_sun = StringField(default='Sunday: 9:00 AM \u2013 6:00 PM')
    footer_copyright = StringField(default='\u00a9 2025 Velvet Steel Barbershop. Quezon City, Philippines.')

    # Social links
    social_links     = StringField(default='[{"icon":"fab fa-facebook-f","label":"Facebook","url":"#"},{"icon":"fab fa-instagram","label":"Instagram","url":"#"},{"icon":"fab fa-tiktok","label":"TikTok","url":"#"}]')

    updated_at       = DateTimeField(default=timezone.now)

    meta = {'collection': 'site_settings'}

    @classmethod
    def get(cls):
        obj = cls.objects().first()
        if obj is None:
            obj = cls()
            obj.save()
        return obj

    def social_list(self):
        import json
        try:
            return json.loads(self.social_links or '[]')
        except Exception:
            return []


class PrivacyPage(Document):
    last_updated   = StringField(default='January 1, 2025')
    intro          = StringField(default='Velvet Steel Barbershop ("we", "our", or "us") is committed to protecting your personal information. This Privacy Policy explains what data we collect when you visit our website or use our online booking system, how we use it, and your rights regarding that data. By using our website, you agree to the practices described in this policy.')
    collect_text   = StringField(default='We collect information you provide directly (name, username, email, profile photo, phone, address) when you create an account or make a booking. We also collect usage data automatically including pages visited, browser type, operating system, IP address, and cookies.')
    use_text       = StringField(default='We use your data to create and manage your account and reservations, send booking confirmations and appointment reminders, respond to inquiries, improve your experience on our site, maintain platform security, and comply with legal obligations under the Philippine Data Privacy Act of 2012 (RA 10173).')
    cookies_text   = StringField(default='We use only strictly necessary cookies to operate this website: sessionid (keeps you logged in), csrftoken (protects forms against cross-site forgery), and vs_cookie_consent (remembers your cookie choice). We do not currently use analytics, advertising, or third-party tracking cookies.')
    sharing_text   = StringField(default='We do not sell, trade, or rent your personal data. We may share information with trusted service providers who help us operate the website (bound by confidentiality), when required by Philippine law or court order, or in a business transfer (with advance notice to you).')
    retention_text = StringField(default='We retain your personal data for as long as your account is active or as needed to provide our services. Reservation records are kept for a minimum of three (3) years as required under Philippine law. You may request deletion of your account at any time.')
    rights_text    = StringField(default='Under the Philippine Data Privacy Act of 2012 (RA 10173), you have the right to access, correct, erase, object to processing, and request portability of your data. You may also file a complaint with the National Privacy Commission (NPC) at privacy.gov.ph. Contact us to exercise any of these rights — we respond within 15 business days.')
    security_text  = StringField(default='We implement industry-standard security including HTTPS encryption, hashed passwords, and CSRF protection. No system is completely secure — we encourage you to use a strong, unique password and log out after each session on shared devices.')
    children_text  = StringField(default='Our website is not directed at children under 13. We do not knowingly collect personal information from children. If you believe a child has provided us with their data, please contact us immediately and we will delete it promptly.')
    changes_text   = StringField(default='We may update this Privacy Policy from time to time. When we do, we will revise the "Last updated" date at the top of this page. Continued use of our website after changes constitutes your acceptance of the updated policy.')
    updated_at     = DateTimeField(default=timezone.now)

    meta = {'collection': 'privacy_page_content'}

    @classmethod
    def get(cls):
        obj = cls.objects().first()
        if obj is None:
            obj = cls()
            obj.save()
        return obj


class TermsPage(Document):
    last_updated    = StringField(default='January 1, 2025')
    intro           = StringField(default='Welcome to Velvet Steel Barbershop. These Terms of Service ("Terms") govern your access to and use of our website and our online appointment booking platform (the "Service"). By accessing or using the site, you agree to be bound by these Terms and our Privacy Policy.')
    acceptance_text = StringField(default='By creating an account, making a booking, or browsing this website, you confirm that you are at least 13 years of age and have the legal capacity to enter into these Terms. If you are using the site on behalf of an organisation, you represent that you have authority to bind that organisation to these Terms.')
    services_text   = StringField(default='Velvet Steel Barbershop provides an informational website describing our services, team, and location; an online appointment booking platform for registered users to schedule and manage reservations; and a customer account system for tracking booking history and loyalty points. We may modify, suspend, or discontinue any aspect of the Service at any time.')
    accounts_text   = StringField(default='To make a booking, you must create an account with accurate, current, and complete information. You are responsible for maintaining the security of your password and all activity under your account. Notify us immediately of any suspected unauthorised access. Do not create multiple accounts, share your account, or use another person\'s account without permission.')
    bookings_text   = StringField(default='Bookings are confirmed when you receive a confirmation from us. We ask that you cancel or reschedule at least 24 hours before your appointment. Repeated no-shows without notice may result in restrictions on future bookings. Prices displayed on the website are indicative and the final price is confirmed at the time of your appointment. All fees are collected in person at the shop.')
    conduct_text    = StringField(default='You agree not to upload harmful, defamatory, or illegal content; impersonate any person; attempt unauthorised access to our systems; use bots or scrapers to extract data; submit false or spam reviews or bookings; or engage in activity that disrupts the normal operation of the site. Violations may result in immediate account termination.')
    ip_text         = StringField(default='All content on this website — text, images, logos, graphics, and software — is the property of Velvet Steel Barbershop and protected by Philippine and international intellectual property laws. You may not reproduce or distribute content without our written consent. By submitting a review, you grant us a non-exclusive, royalty-free licence to display that content on our website and marketing materials.')
    disclaimers_text = StringField(default='The site and Service are provided on an "as is" and "as available" basis without warranties of any kind. We disclaim all implied warranties including merchantability, fitness for a particular purpose, and non-infringement. We do not warrant that the site will be uninterrupted, error-free, or free of harmful components.')
    liability_text  = StringField(default='To the maximum extent permitted by Philippine law, Velvet Steel Barbershop and its owners, employees, and affiliates shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the site. Our total liability to you shall not exceed the amount you paid us in the three (3) months preceding the claim, or ₱1,000.00, whichever is greater.')
    governing_text  = StringField(default='These Terms are governed by and construed in accordance with the laws of the Republic of the Philippines. Any disputes shall be subject to the exclusive jurisdiction of the courts of Quezon City, Metro Manila, Philippines.')
    changes_text    = StringField(default='We reserve the right to update these Terms at any time. Changes take effect immediately upon posting and the "Last updated" date will be revised. Continued use of the site after changes constitutes your acceptance of the revised Terms.')
    updated_at      = DateTimeField(default=timezone.now)

    meta = {'collection': 'terms_page_content'}

    @classmethod
    def get(cls):
        obj = cls.objects().first()
        if obj is None:
            obj = cls()
            obj.save()
        return obj
