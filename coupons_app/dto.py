from dataclasses import dataclass
from decimal import Decimal

from coupons_app.models import Product


@dataclass
class OrderItemData:
    """Input data for an order item, containing product ID and quantity."""

    product_id: int
    quantity: int


@dataclass
class EnrichedOrderItem:
    """Order item data enriched with product details and discount information."""

    product: Product
    quantity: int
    price_per_item: Decimal
    discount_amount: Decimal


@dataclass
class OrderTotals:
    """Calculated totals for an order, including original total, discounted total, and enriched items."""

    original_total: Decimal
    discounted_total: Decimal
    items: list[EnrichedOrderItem]
