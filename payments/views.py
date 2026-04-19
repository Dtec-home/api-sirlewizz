import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import MpesaTransaction
from orders.models import Order


@csrf_exempt
@require_POST
def daraja_callback(request):
    try:
        body = json.loads(request.body)
        result = body.get('Body', {}).get('stkCallback', {})
        checkout_request_id = result.get('CheckoutRequestID', '')
        result_code = str(result.get('ResultCode', ''))
        result_desc = result.get('ResultDesc', '')

        try:
            tx = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
        except MpesaTransaction.DoesNotExist:
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Unknown transaction'})

        tx.result_code = result_code
        tx.result_desc = result_desc

        if result_code == '0':
            # Extract receipt from callback metadata
            items = result.get('CallbackMetadata', {}).get('Item', [])
            receipt = next((i['Value'] for i in items if i['Name'] == 'MpesaReceiptNumber'), '')
            tx.mpesa_receipt_number = receipt
            tx.status = MpesaTransaction.Status.COMPLETED
            tx.order.status = Order.Status.CONFIRMED
            tx.order.save(update_fields=['status'])
        else:
            tx.status = MpesaTransaction.Status.FAILED
            tx.order.status = Order.Status.FAILED
            tx.order.save(update_fields=['status'])

        tx.save()
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

    except Exception as e:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)}, status=500)
