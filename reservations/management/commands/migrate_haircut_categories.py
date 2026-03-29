from django.core.management.base import BaseCommand
from reservations.models import HaircutStyle
from decimal import Decimal

def price_to_tier(price):
    try:
        p = float(price or 0)
    except Exception:
        return 'styled'
    if p <= 100:
        return 'basic'
    elif p <= 200:
        return 'finish'
    elif p <= 350:
        return 'styled'
    elif p <= 600:
        return 'fade'
    else:
        return 'premium'


NEW_CATEGORIES = {'basic', 'finish', 'styled', 'fade', 'premium'}


class Command(BaseCommand):
    help = 'Migrates old haircut style category values to new price-tier categories'

    def handle(self, *args, **kwargs):
        styles = HaircutStyle.objects.all()
        migrated = 0
        skipped  = 0

        for style in styles:
            if style.category in NEW_CATEGORIES:
                skipped += 1
                continue
            old_cat      = style.category
            style.category = price_to_tier(style.price)
            style.save()
            self.stdout.write(
                f'  [{style.name}]  {old_cat!r} → {style.category!r}  (₱{style.price})'
            )
            migrated += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {migrated} migrated, {skipped} already up-to-date.'
        ))