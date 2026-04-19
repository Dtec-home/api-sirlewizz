from django.contrib import admin
from .models import StockEntry, StockAlert


@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('variant', 'entry_type', 'quantity', 'created_by', 'created_at')
    list_filter = ('entry_type',)
    search_fields = ('variant__sku', 'variant__product__name')


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ('variant', 'current_stock', 'threshold', 'resolved', 'created_at')
    list_filter = ('resolved',)
