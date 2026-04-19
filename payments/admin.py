from django.contrib import admin
from .models import MpesaTransaction


@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'phone_number', 'amount', 'status', 'mpesa_receipt_number', 'created_at')
    list_filter = ('status',)
    search_fields = ('phone_number', 'mpesa_receipt_number', 'checkout_request_id')
    readonly_fields = ('checkout_request_id', 'merchant_request_id', 'mpesa_receipt_number',
                       'result_code', 'result_desc', 'created_at', 'updated_at')
