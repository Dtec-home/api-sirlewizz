import strawberry
from typing import Optional
from .types import (
    OrderType, MpesaTransactionType, StockEntryType,
    ProductType, OrderInput, ProductInput, StockUpdateInput,
)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_order(self, input: OrderInput) -> OrderType:
        from orders.services import create_order
        return create_order(input)

    @strawberry.mutation
    def initiate_mpesa_payment(self, order_id: int, phone: str) -> MpesaTransactionType:
        from payments.daraja import initiate_stk_push
        return initiate_stk_push(order_id, phone)

    @strawberry.mutation
    def update_stock(self, input: StockUpdateInput) -> StockEntryType:
        from products.models import Variant
        from inventory.models import StockEntry
        variant = Variant.objects.get(pk=input.variant_id)
        entry = StockEntry.objects.create(
            variant=variant,
            entry_type=input.entry_type,
            quantity=input.quantity,
            note=input.note,
        )
        # Apply stock change
        if input.entry_type == 'in':
            variant.stock += input.quantity
        elif input.entry_type == 'out':
            variant.stock = max(0, variant.stock - input.quantity)
        else:
            variant.stock = input.quantity
        variant.save(update_fields=['stock'])
        return entry

    @strawberry.mutation
    def upsert_product(self, id: Optional[int] = None, input: ProductInput = None) -> ProductType:
        from products.models import Product, Category
        from django.utils.text import slugify
        category = Category.objects.get(pk=input.category_id)
        if id:
            product = Product.objects.get(pk=id)
            product.name = input.name
            product.description = input.description
            product.category = category
            product.price = input.price
            product.featured = input.featured
            product.save()
        else:
            product = Product.objects.create(
                name=input.name,
                slug=slugify(input.name),
                description=input.description,
                category=category,
                price=input.price,
                featured=input.featured,
            )
        return product
