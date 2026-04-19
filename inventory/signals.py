from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StockEntry, StockAlert


@receiver(post_save, sender=StockEntry)
def check_low_stock(sender, instance, created, **kwargs):
    if not created:
        return
    variant = instance.variant
    threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 5)
    if variant.stock <= threshold:
        # Resolve any existing open alert first
        StockAlert.objects.filter(variant=variant, resolved=False).update(resolved=True)
        StockAlert.objects.create(
            variant=variant,
            threshold=threshold,
            current_stock=variant.stock,
        )
