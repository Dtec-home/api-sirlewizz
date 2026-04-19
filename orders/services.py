from django.db import transaction
from products.models import Variant
from .models import Order, OrderItem


@transaction.atomic
def create_order(input) -> Order:
    """
    Validates stock, creates Order + OrderItems, decrements variant stock.
    Raises ValueError if any variant has insufficient stock.
    """
    total = 0
    line_items = []

    for item_input in input.items:
        variant = Variant.objects.select_for_update().get(pk=item_input.variant_id)
        if variant.stock < item_input.quantity:
            raise ValueError(
                f"Insufficient stock for {variant}: requested {item_input.quantity}, available {variant.stock}"
            )
        subtotal = variant.product.price * item_input.quantity
        total += subtotal
        line_items.append((variant, item_input.quantity, variant.product.price))

    order = Order.objects.create(
        customer_name=input.customer_name,
        customer_email=input.customer_email,
        customer_phone=input.customer_phone,
        delivery_address=input.delivery_address,
        total_amount=total,
    )

    for variant, qty, price in line_items:
        OrderItem.objects.create(order=order, variant=variant, quantity=qty, unit_price=price)
        variant.stock -= qty
        variant.save(update_fields=['stock'])

    return order
