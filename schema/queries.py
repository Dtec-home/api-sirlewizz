import strawberry
from typing import Optional, List
from datetime import date
from django.db.models import Sum, Q
from products.models import Category, Product
from inventory.models import StockEntry, StockAlert
from orders.models import Order
from payments.models import MpesaTransaction
from .types import (
    CategoryType, ProductType, ProductConnection,
    StockEntryType, StockAlertType, OrderType,
    MpesaTransactionType, PaymentStatusType, SalesReportType,
)


@strawberry.type
class Query:
    @strawberry.field
    def categories(self) -> List[CategoryType]:
        return Category.objects.all()

    @strawberry.field
    def products(
        self,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 12,
    ) -> ProductConnection:
        qs = Product.objects.select_related('category').prefetch_related('variants', 'images')
        if category:
            qs = qs.filter(category__slug=category)
        total = qs.count()
        offset = (page - 1) * page_size
        items = list(qs[offset: offset + page_size])
        return ProductConnection(items=items, total=total, has_next=(offset + page_size) < total)

    @strawberry.field
    def product(self, slug: str) -> Optional[ProductType]:
        try:
            return Product.objects.select_related('category').prefetch_related('variants', 'images').get(slug=slug)
        except Product.DoesNotExist:
            return None

    @strawberry.field
    def products_by_category(
        self, slug: str, page: int = 1, page_size: int = 12
    ) -> ProductConnection:
        qs = Product.objects.filter(category__slug=slug).select_related('category').prefetch_related('variants', 'images')
        total = qs.count()
        offset = (page - 1) * page_size
        items = list(qs[offset: offset + page_size])
        return ProductConnection(items=items, total=total, has_next=(offset + page_size) < total)

    @strawberry.field
    def inventory_items(self, low_stock: bool = False) -> List[StockEntryType]:
        from django.conf import settings
        threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 5)
        qs = StockEntry.objects.select_related('variant__product')
        if low_stock:
            qs = qs.filter(variant__stock__lte=threshold)
        return qs[:100]

    @strawberry.field
    def stock_alerts(self, resolved: bool = False) -> List[StockAlertType]:
        return StockAlert.objects.filter(resolved=resolved).select_related('variant__product')

    @strawberry.field
    def order_payment_status(self, order_id: int) -> Optional[PaymentStatusType]:
        try:
            order = Order.objects.get(pk=order_id)
            tx = getattr(order, 'mpesa_transaction', None)
            return PaymentStatusType(
                order_id=order.id,
                payment_status=tx.status if tx else 'pending',
                mpesa_receipt=tx.mpesa_receipt_number if tx else None,
            )
        except Order.DoesNotExist:
            return None

    @strawberry.field
    def sales_report(
        self,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> SalesReportType:
        qs = Order.objects.all()
        if from_date:
            qs = qs.filter(created_at__date__gte=from_date)
        if to_date:
            qs = qs.filter(created_at__date__lte=to_date)
        total_revenue = qs.filter(status='confirmed').aggregate(t=Sum('total_amount'))['t'] or 0
        return SalesReportType(
            total_revenue=total_revenue,
            total_orders=qs.count(),
            confirmed_orders=qs.filter(status='confirmed').count(),
            pending_orders=qs.filter(status='pending').count(),
            failed_orders=qs.filter(status='failed').count(),
        )

    @strawberry.field
    def recent_orders(self, limit: int = 10) -> List[OrderType]:
        return Order.objects.prefetch_related('items__variant__product')[:limit]

    @strawberry.field
    def mpesa_transactions(self, status: Optional[str] = None) -> List[MpesaTransactionType]:
        qs = MpesaTransaction.objects.select_related('order')
        if status:
            qs = qs.filter(status=status)
        return qs[:100]
