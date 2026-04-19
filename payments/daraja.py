import requests
import base64
from datetime import datetime
from django.conf import settings


DARAJA_BASE = (
    'https://sandbox.safaricom.co.ke'
    if settings.MPESA_ENV == 'sandbox'
    else 'https://api.safaricom.co.ke'
)


def _get_access_token() -> str:
    auth = base64.b64encode(
        f"{settings.MPESA_CONSUMER_KEY}:{settings.MPESA_CONSUMER_SECRET}".encode()
    ).decode()
    resp = requests.get(
        f"{DARAJA_BASE}/oauth/v1/generate?grant_type=client_credentials",
        headers={'Authorization': f'Basic {auth}'},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()['access_token']


def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d%H%M%S')


def _password(timestamp: str) -> str:
    raw = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def format_phone(phone: str) -> str:
    clean = phone.replace(' ', '').replace('-', '')
    if clean.startswith('+254'):
        return clean[1:]
    if clean.startswith('0'):
        return '254' + clean[1:]
    return clean


def initiate_stk_push(order_id: int, phone: str):
    from orders.models import Order
    from payments.models import MpesaTransaction

    order = Order.objects.get(pk=order_id)
    formatted_phone = format_phone(phone)
    token = _get_access_token()
    ts = _timestamp()

    payload = {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': _password(ts),
        'Timestamp': ts,
        'TransactionType': 'CustomerBuyGoodsOnline',
        'Amount': order.total_amount,
        'PartyA': formatted_phone,
        'PartyB': settings.MPESA_TILL_NUMBER,
        'PhoneNumber': formatted_phone,
        'CallBackURL': settings.MPESA_CALLBACK_URL,
        'AccountReference': str(order_id),
        'TransactionDesc': f'Order {order_id}',
    }

    resp = requests.post(
        f"{DARAJA_BASE}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    tx, _ = MpesaTransaction.objects.update_or_create(
        order=order,
        defaults={
            'phone_number': formatted_phone,
            'amount': order.total_amount,
            'checkout_request_id': data.get('CheckoutRequestID', ''),
            'merchant_request_id': data.get('MerchantRequestID', ''),
            'status': MpesaTransaction.Status.PENDING,
        },
    )
    return tx
