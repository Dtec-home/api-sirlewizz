from django.db import models
from django.conf import settings
from products.models import Variant


class StockEntry(models.Model):
    class EntryType(models.TextChoices):
        IN = 'in', 'Stock In'
        OUT = 'out', 'Stock Out'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='stock_entries')
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    quantity = models.IntegerField()
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'stock entries'

    def __str__(self):
        return f"{self.entry_type} {self.quantity} — {self.variant}"


class StockAlert(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='alerts')
    threshold = models.PositiveIntegerField()
    current_stock = models.PositiveIntegerField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.variant} at {self.current_stock} units"
