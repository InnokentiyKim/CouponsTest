from decimal import Decimal

import pytest
from rest_framework.exceptions import NotFound, ValidationError

from coupons_app.dto import OrderItemData
from coupons_app.models import CouponUsage, Order, OrderItem
from coupons_app.services import CouponService, OrderService, UserService
from rest import errocodes as errors


@pytest.mark.django_db
class TestUserService:
    """Tests for UserService methods."""
    def test_get_user_success(self, user):
        """Checks that get_user returns the correct User instance when it exists."""
        fetched = UserService.get_user(user.id)
        assert fetched.pk == user.pk

    def test_get_user_not_found(self, db):
        """Checks that get_user raises NotFound when the user does not exist."""
        with pytest.raises(errors.ItemNotFoundException):
            UserService.get_user(99999)


@pytest.mark.django_db
class TestCouponServiceValidation:
    """Tests for CouponService.validate_coupon method covering various validation scenarios:"""
    def test_validate_coupon_success(self, user, product, valid_coupon):
        """Valid coupon: should return the Coupon instance."""
        coupon = CouponService.validate_coupon(
            code="SALE10", user=user, products=[product]
        )
        assert coupon.pk == valid_coupon.pk

    def test_validate_coupon_not_found(self, user, product):
        """Non-existent coupon code: should raise ValidationError."""
        with pytest.raises(errors.ItemNotFoundException, match="не найден"):
            CouponService.validate_coupon(
                code="NONEXISTENT", user=user, products=[product]
            )

    def test_validate_coupon_expired(self, user, product, expired_coupon):
        """Expired coupon: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="просрочен"):
            CouponService.validate_coupon(
                code="EXPIRED5", user=user, products=[product]
            )

    def test_validate_coupon_not_yet_active(self, user, product, future_coupon):
        """Valid coupon with start_date in the future: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="просрочен"):
            CouponService.validate_coupon(
                code="FUTURE50", user=user, products=[product]
            )

    def test_validate_coupon_usage_limit_reached(self, user, product, exhausted_coupon):
        """Coupon that has reached max_usages: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="лимит"):
            CouponService.validate_coupon(
                code="MAXED_OUT", user=user, products=[product]
            )

    def test_validate_coupon_already_used_by_user(
        self, user, product, valid_coupon, used_coupon_for_user
    ):
        """User has already used this coupon: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="уже использовали"):
            CouponService.validate_coupon(code="SALE10", user=user, products=[product])

    def test_validate_coupon_another_user_can_use(
        self, another_user, product, valid_coupon, used_coupon_for_user
    ):
        """Coupon used by one user should still be valid for another user."""
        coupon = CouponService.validate_coupon(
            code="SALE10", user=another_user, products=[product]
        )
        assert coupon.pk == valid_coupon.pk

    def test_validate_coupon_category_mismatch(
        self, user, product_another_category, category_coupon
    ):
        """Category-restricted coupon. Should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="категории"):
            CouponService.validate_coupon(
                code="ELECTRONICS20",
                user=user,
                products=[product_another_category],
            )

    def test_validate_coupon_category_match(self, user, product, category_coupon):
        """Category-restricted coupon with matching product category: should be valid."""
        coupon = CouponService.validate_coupon(
            code="ELECTRONICS20", user=user, products=[product]
        )
        assert coupon.pk == category_coupon.pk

    def test_validate_coupon_no_category_restriction(
        self, user, product_another_category, valid_coupon
    ):
        """Coupon without category restriction should be valid for any product."""
        coupon = CouponService.validate_coupon(
            code="SALE10",
            user=user,
            products=[product_another_category],
        )
        assert coupon.pk == valid_coupon.pk


@pytest.mark.django_db
class TestOrderServiceCalculateTotals:
    """Tests for OrderService._calculate_totals method covering various scenarios of coupon application and product eligibility."""
    def test_no_coupon(self, product):
        """Coupon is None: no discount, totals equal original price."""
        items_data = [OrderItemData(product_id=product.id, quantity=2)]
        products_map = {product.id: product}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=None
        )

        assert order_totals.original_total == Decimal("2000.00")
        assert order_totals.discounted_total == Decimal("2000.00")
        assert order_totals.items[0].discount_amount == Decimal("0.00")

    def test_with_coupon(self, product, valid_coupon):
        """Valid coupon: discount applied to eligible product."""
        items_data = [OrderItemData(product_id=product.id, quantity=1)]
        products_map = {product.id: product}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=valid_coupon
        )

        assert order_totals.original_total == Decimal("1000.00")
        assert order_totals.discounted_total == Decimal("900.00")
        assert order_totals.items[0].discount_amount == Decimal("100.00")

    def test_promo_excluded_product(self, promo_excluded_product, valid_coupon):
        """Promo-excluded product: no discount applied even if coupon is valid."""
        items_data = [OrderItemData(product_id=promo_excluded_product.id, quantity=1)]
        products_map = {promo_excluded_product.id: promo_excluded_product}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=valid_coupon
        )

        assert order_totals.original_total == Decimal("5000.00")
        assert order_totals.discounted_total == Decimal("5000.00")
        assert order_totals.items[0].discount_amount == Decimal("0.00")

    def test_category_coupon_matching(self, product, category_coupon):
        """Category coupon — discount applies to product of matching category."""
        items_data = [OrderItemData(product_id=product.id, quantity=1)]
        products_map = {product.id: product}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=category_coupon
        )

        assert order_totals.original_total == Decimal("1000.00")
        assert order_totals.discounted_total == Decimal("800.00") # 20% скидка
        assert order_totals.items[0].discount_amount == Decimal("200.00")

    def test_category_coupon_no_match(self, product_another_category, category_coupon):
        """Category coupon — no discount for product of different category."""
        items_data = [OrderItemData(product_id=product_another_category.id, quantity=1)]
        products_map = {product_another_category.id: product_another_category}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=category_coupon
        )

        assert order_totals.original_total == Decimal("2000.00")
        assert order_totals.discounted_total == Decimal("2000.00")
        assert order_totals.items[0].discount_amount == Decimal("0.00")

    def test_mixed_cart(
        self,
        product,
        promo_excluded_product,
        product_another_category,
        category_coupon,
    ):
        """Mixed cart with category coupon: discount applies only to eligible product."""
        items_data = [
            OrderItemData(product_id=product.id, quantity=1),
            OrderItemData(product_id=promo_excluded_product.id, quantity=1),
            OrderItemData(product_id=product_another_category.id, quantity=1),
        ]
        products_map = {
            product.id: product,
            promo_excluded_product.id: promo_excluded_product,
            product_another_category.id: product_another_category,
        }

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=category_coupon
        )

        # original: 1000 + 5000 + 2000 = 8000
        assert order_totals.original_total == Decimal("8000.00")
        # Скидка только на product (Электроника, не excluded): 1000 * 0.20 = 200
        # promo_excluded: 0, другая категория: 0
        assert order_totals.discounted_total == Decimal("7800.00")
        assert order_totals.items[0].discount_amount == Decimal("200.00")
        assert order_totals.items[1].discount_amount == Decimal("0.00")
        assert order_totals.items[2].discount_amount == Decimal("0.00")

    def test_100_percent_discount(self, product, full_discount_coupon):
        """Coupon with 100% discount: discounted total should be zero, discount amount equals original price."""
        items_data = [OrderItemData(product_id=product.id, quantity=1)]
        products_map = {product.id: product}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=full_discount_coupon
        )

        assert order_totals.original_total == Decimal("1000.00")
        assert order_totals.discounted_total == Decimal("0.00")
        assert order_totals.items[0].discount_amount == Decimal("1000.00")

    def test_multiple_quantities(self, product, valid_coupon):
        """Discount should be calculated on price * quantity."""
        items_data = [OrderItemData(product_id=product.id, quantity=5)]
        products_map = {product.id: product}

        order_totals = OrderService._calculate_totals(
            items_data, products_map, coupon=valid_coupon
        )

        assert order_totals.original_total == Decimal("5000.00")
        # 10% от 5000 = 500
        assert order_totals.discounted_total == Decimal("4500.00")
        assert order_totals.items[0].discount_amount == Decimal("500.00")


@pytest.mark.django_db
class TestOrderServiceCreateOrder:
    """Tests for OrderService.create_order method covering order creation with and without coupons."""
    def test_create_order_without_coupon(self, user, product):
        """Order creation without coupon: should create order with correct totals and no coupon applied."""
        order = OrderService.create_order(
            user_id=user.id,
            items_data=[OrderItemData(product_id=product.id, quantity=2)],
        )

        assert order.user_id == user.id
        assert order.coupon is None
        assert order.original_total == Decimal("2000.00")
        assert order.discounted_total == Decimal("2000.00")

    def test_create_order_with_valid_coupon(self, user, product, valid_coupon):
        """Order creation with valid coupon: should apply discount and associate coupon with order."""
        order = OrderService.create_order(
            user_id=user.id,
            items_data=[OrderItemData(product_id=product.id, quantity=1)],
            coupon_code="SALE10",
        )

        assert order.coupon_id == valid_coupon.id
        assert order.original_total == Decimal("1000.00")
        assert order.discounted_total == Decimal("900.00")

    def test_coupon_usage_count_incremented(self, user, product, valid_coupon):
        """On successful order creation with a coupon, the coupon's usage_count should be incremented."""
        OrderService.create_order(
            user_id=user.id,
            items_data=[OrderItemData(product_id=product.id, quantity=1)],
            coupon_code="SALE10",
        )

        valid_coupon.refresh_from_db()
        assert valid_coupon.usage_count == 1

    def test_coupon_usage_record_created(self, user, product, valid_coupon):
        """On successful order creation with a coupon, a CouponUsage record should be created for the user and coupon."""
        OrderService.create_order(
            user_id=user.id,
            items_data=[OrderItemData(product_id=product.id, quantity=1)],
            coupon_code="SALE10",
        )

        assert CouponUsage.objects.filter(user=user, coupon=valid_coupon).exists()

    def test_user_not_found(self, product):
        """Non-existent user_id: should raise NotFound."""
        with pytest.raises(errors.ItemNotFoundException):
            OrderService.create_order(
                user_id=99999,
                items_data=[OrderItemData(product_id=product.id, quantity=1)],
            )

    def test_product_not_found(self, user):
        """Non-existent product_id in items_data: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="не найдены"):
            OrderService.create_order(
                user_id=user.id,
                items_data=[OrderItemData(product_id=99999, quantity=1)],
            )

    def test_expired_coupon(self, user, product, expired_coupon):
        """Expired coupon code: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="просрочен"):
            OrderService.create_order(
                user_id=user.id,
                items_data=[OrderItemData(product_id=product.id, quantity=1)],
                coupon_code="EXPIRED5",
            )

    def test_exhausted_coupon(self, user, product, exhausted_coupon):
        """Coupon that has reached max_usages: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="лимит"):
            OrderService.create_order(
                user_id=user.id,
                items_data=[OrderItemData(product_id=product.id, quantity=1)],
                coupon_code="MAXED_OUT",
            )

    def test_duplicate_coupon_usage(
        self, user, product, valid_coupon, used_coupon_for_user
    ):
        """User has already used this coupon: should raise ValidationError."""
        with pytest.raises(errors.InvalidItemsDataException, match="уже использовали"):
            OrderService.create_order(
                user_id=user.id,
                items_data=[OrderItemData(product_id=product.id, quantity=1)],
                coupon_code="SALE10",
            )

    def test_atomicity_on_coupon_failure(self, user, product, expired_coupon):
        """If coupon validation fails, no order or order items should be created (atomic transaction)."""
        orders_before = Order.objects.count()
        items_before = OrderItem.objects.count()

        with pytest.raises(errors.InvalidItemsDataException):
            OrderService.create_order(
                user_id=user.id,
                items_data=[OrderItemData(product_id=product.id, quantity=1)],
                coupon_code="EXPIRED5",
            )

        assert Order.objects.count() == orders_before
        assert OrderItem.objects.count() == items_before

    def test_multiple_items(self, user, product, expensive_product):
        """Order with multiple items: totals should be calculated correctly without coupon."""
        order = OrderService.create_order(
            user_id=user.id,
            items_data=[
                OrderItemData(product_id=product.id, quantity=1),
                OrderItemData(product_id=expensive_product.id, quantity=2),
            ],
        )

        assert order.original_total == Decimal("101000.00")
        assert order.discounted_total == Decimal("101000.00")

    def test_two_users_same_coupon(self, user, another_user, product, valid_coupon):
        """Two different users can use the same valid coupon, and usage_count should reflect both usages."""
        order1 = OrderService.create_order(
            user_id=user.id,
            items_data=[OrderItemData(product_id=product.id, quantity=1)],
            coupon_code="SALE10",
        )
        order2 = OrderService.create_order(
            user_id=another_user.id,
            items_data=[OrderItemData(product_id=product.id, quantity=1)],
            coupon_code="SALE10",
        )

        assert order1.coupon_id == valid_coupon.id
        assert order2.coupon_id == valid_coupon.id

        valid_coupon.refresh_from_db()
        assert valid_coupon.usage_count == 2

    def test_promo_excluded_product_in_order_with_coupon(
        self, user, product, promo_excluded_product, valid_coupon
    ):
        """Order with a promo-excluded product and a valid coupon: discount should apply only to eligible product."""
        order = OrderService.create_order(
            user_id=user.id,
            items_data=[
                OrderItemData(product_id=product.id, quantity=1),
                OrderItemData(product_id=promo_excluded_product.id, quantity=1),
            ],
            coupon_code="SALE10",
        )

        assert order.original_total == Decimal("6000.00") # original: 1000 + 5000 = 6000
        assert order.discounted_total == Decimal("5900.00") # discounted: 900 + 5000 = 5900
