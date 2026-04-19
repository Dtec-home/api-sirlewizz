import strawberry
import strawberry_django
from strawberry import auto
from strawberry.types import Info
from typing import Optional, List
from products.models import Category, Product, Variant, ProductImage
from inventory.models import StockEntry, StockAlert
from orders.models import Order, OrderItem
from payments.models import MpesaTransaction


@strawberry_django.type(Category)
class CategoryType:
    id: auto
    name: auto
    slug: auto
    description: auto


@strawberry_django.type(ProductImage)
class ProductImageType:
    id: auto
    order: auto

    @strawberry.field
    def image(self, info: Info) -> str:
        if not self.image:
            return ''
        url = self.image.url
        # Return absolute URL so the frontend doesn't request from localhost:3000
        if url.startswith('/'):
            request = info.context.get('request')
            if request:
                return request.build_absolute_uri(url)
            from django.conf import settings
            base = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            return f"{base}{url}"
        return url


@strawberry_django.type(Variant)
class VariantType:
    id: auto
    size: auto
    color: auto
    stock: auto
    sku: auto


@strawberry_django.type(Product)
class ProductType:
    id: auto
    name: auto
    slug: auto
    description: auto
    price: auto
    featured: auto
    created_at: auto
    category: CategoryType
    variants: List[VariantType]
    images: List[ProductImageType]

    @strawberry.field
    def stock(self) -> int:
        return sum(v.stock for v in self.variants.all())

    @strawberry.field
    def related_products(self) -> List['ProductType']:
        return Product.objects.filter(category=self.category).exclude(id=self.id)[:4]


@strawberry.type
class ProductConnection:
    items: List[ProductType]
    total: int
    has_next: bool


@strawberry_django.type(StockEntry)
class StockEntryType:
    id: auto
    entry_type: auto
    quantity: auto
    note: auto
    created_at: auto
    variant: VariantType


@strawberry_django.type(StockAlert)
class StockAlertType:
    id: auto
    current_stock: auto
    threshold: auto
    resolved: auto
    created_at: auto
    variant: VariantType


@strawberry_django.type(OrderItem)
class OrderItemType:
    id: auto
    quantity: auto
    unit_price: auto
    variant: VariantType

    @strawberry.field
    def subtotal(self) -> int:
        return self.quantity * self.unit_price


@strawberry_django.type(Order)
class OrderType:
    id: auto
    customer_name: auto
    customer_email: auto
    customer_phone: auto
    delivery_address: auto
    status: auto
    total_amount: auto
    created_at: auto
    items: List[OrderItemType]


@strawberry_django.type(MpesaTransaction)
class MpesaTransactionType:
    id: auto
    phone_number: auto
    amount: auto
    checkout_request_id: auto
    mpesa_receipt_number: auto
    status: auto
    created_at: auto


@strawberry.type
class PaymentStatusType:
    order_id: int
    payment_status: str
    mpesa_receipt: Optional[str]


@strawberry.input
class OrderItemInput:
    variant_id: int
    quantity: int


@strawberry.input
class OrderInput:
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_address: str
    items: List[OrderItemInput]


@strawberry.input
class ProductInput:
    name: str
    description: str
    category_id: int
    price: int
    featured: bool = False


@strawberry.type
class SalesReportType:
    total_revenue: int
    total_orders: int
    confirmed_orders: int
    pending_orders: int
    failed_orders: int


@strawberry.input
class StockUpdateInput:
    variant_id: int
    quantity: int
    entry_type: str
    note: str = ''
