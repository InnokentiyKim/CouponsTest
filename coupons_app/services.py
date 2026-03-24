import logging
from decimal import Decimal
from typing import Any
from rest import errocodes as errors

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from coupons_app.dto import OrderItemData, EnrichedOrderItem, OrderTotals

from coupons_app.models import (
    Coupon,
    CouponUsage,
    Order,
    OrderItem,
    Product,
    User,
)


logger = logging.getLogger(__name__)


class UserService:
    """User management and retrieval service."""

    @staticmethod
    def get_user(user_id: int) -> User:
        """Retrieves a User by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User instance with the given ID.

        Raises:
            NotFound: If no User with the given ID exists.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning("User %s does not exist.", user_id)
            raise errors.ItemNotFoundException(detail=f"Пользователь с id={user_id} не найден.", code="User not found")


class CouponService:
    """Service for validating and applying coupons to orders."""

    @staticmethod
    def validate_coupon(code: str, user: User, products: list[Product]) -> Coupon:
        """
        Validates a coupon code for a given user and list of products.

        Args:
            code: The coupon code to validate.
            user: The user attempting to use the coupon.
            products: The list of products in the order.

        Returns:
            The valid Coupon instance corresponding to the code.
        """
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            logger.warning("Coupon %s does not exist.", code)
            raise errors.ItemNotFoundException(detail=f"Промокод «{code}» не найден.", code="Coupon not found")

        if not coupon.is_valid_at(timezone.now()):
            logger.warning("Coupon %s is out of date.", code)
            raise errors.InvalidItemsDataException(detail=f"Промокод «{code}» просрочен.", code="Coupon expired")

        if coupon.usage_count >= coupon.max_usages:
            logger.warning("Coupon %s is exhausted.", code)
            raise errors.InvalidItemsDataException(
                detail=f"Превышен лимит использований промокода.", code="Coupon max usages exceeded"
            )

        if CouponUsage.objects.filter(user=user, coupon=coupon).exists():
            logger.warning("Coupon %s is already used with user %s.", code, user.id)
            raise errors.InvalidItemsDataException(
                detail=f"Вы уже использовали промокод «{code}».", code="Coupon already used"
            )

        if coupon.category_id is not None:
            has_matching = any(p.category_id == coupon.category_id for p in products)
            if not has_matching:
                logger.warning(
                    "Category mismatch for Coupon %s with category %s.",
                    code,
                    coupon.category_id,
                )
                raise errors.InvalidItemsDataException(
                    detail="Промокод не действует на выбранные категории товаров.",
                    code="Coupon category mismatch"
                )

        return coupon


class OrderService:
    """Service for creating orders, calculating totals, and applying coupons."""

    @staticmethod
    def _calculate_totals(
        items_data: list[OrderItemData],
        products_map: dict[int, Product],
        coupon: Coupon | None = None,
    ) -> OrderTotals:
        """
        Calculates the original and discounted totals for an order, along with enriched item details.

        Args:
            items_data: List of order item data containing product IDs and quantities.
            products_map: A mapping of product IDs to Product instances for quick lookup.
            coupon: An optional Coupon instance to apply discounts from.

        Returns:
            An OrderTotals instance containing the original total, discounted total, and enriched items.
        """
        original_total = Decimal("0.00")
        discounted_total = Decimal("0.00")
        enriched_items: list[EnrichedOrderItem] | list[Any] = []

        discount_rate = (
            coupon.discount_percent / Decimal("100") if coupon else Decimal("0")
        )

        for item in items_data:
            product = products_map[item.product_id]
            quantity = item.quantity
            line_total = product.price * quantity
            original_total += line_total

            discount_amount = Decimal("0.00")
            if coupon and not product.is_promo_excluded:
                category_matches = (
                    coupon.category_id is None
                    or coupon.category_id == product.category_id
                )
                if category_matches:
                    discount_amount = (line_total * discount_rate).quantize(
                        Decimal("0.01")
                    )

            discounted_total += line_total - discount_amount

            enriched_items.append(
                EnrichedOrderItem(
                    product=product,
                    quantity=quantity,
                    price_per_item=product.price,
                    discount_amount=discount_amount,
                )
            )

        return OrderTotals(
            original_total=original_total,
            discounted_total=discounted_total,
            items=enriched_items,
        )

    @classmethod
    def create_order(
        cls,
        user_id: int,
        items_data: list[OrderItemData],
        coupon_code: str | None = None,
    ) -> Order:
        """
        Creates an order for a user with the given items and an optional coupon code.
        This method performs the following steps:
        1. Retrieves the user by ID.
        2. Fetches the products corresponding to the item data.
        3. Validates the coupon code if provided.
        4. Calculates the original and discounted totals.
        5. Creates the Order and associated OrderItems.
        6. Records the coupon usage if a coupon was applied.

        Args:
            user_id: The ID of the user placing the order.
            items_data: A list of OrderItemData containing product IDs and quantities.
            coupon_code: An optional coupon code to apply to the order.

        Returns:
            The created Order instance with related items prefetched for response serialization.
        """
        with transaction.atomic():
            user = UserService.get_user(user_id)

            product_ids = [item.product_id for item in items_data]
            products = list(Product.objects.filter(id__in=product_ids))
            products_map = {p.id: p for p in products}

            missing_ids = set(product_ids) - set(products_map.keys())
            if missing_ids:
                raise errors.InvalidItemsDataException(
                    detail=f"Товары с id {sorted(missing_ids)} не найдены.", code="Some products not found"
                )

            coupon = None
            if coupon_code:
                coupon = CouponService.validate_coupon(
                    code=coupon_code, user=user, products=products
                )

            totals = cls._calculate_totals(
                items_data=items_data,
                products_map=products_map,
                coupon=coupon,
            )

            order = Order.objects.create(
                user=user,
                coupon=coupon,
                original_total=totals.original_total,
                discounted_total=totals.discounted_total,
            )

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_per_item=item.price_per_item,
                    discount_amount=item.discount_amount,
                )
                for item in totals.items
            ]
            OrderItem.objects.bulk_create(order_items)

            if coupon:
                CouponUsage.objects.create(user=user, coupon=coupon)
                Coupon.objects.filter(pk=coupon.pk).update(
                    usage_count=F("usage_count") + 1
                )

        return Order.objects.prefetch_related("items__product").get(pk=order.pk)
