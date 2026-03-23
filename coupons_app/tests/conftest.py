from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from coupons_app.models import (
    Category,
    Coupon,
    CouponUsage,
    Product,
    User,
)


@pytest.fixture()
def api_client() -> APIClient:
    """DRF APIClient for making test requests."""
    return APIClient()


@pytest.fixture()
def user() -> User:
    """Common user instance with email for testing."""
    return User.objects.create(
        email="ivan@example.com",
        first_name="Иван",
        last_name="Петров",
    )


@pytest.fixture()
def another_user() -> User:
    """Second user instance for testing."""
    return User.objects.create(
        email="anna@example.com",
        first_name="Анна",
        last_name="Сидорова",
    )


@pytest.fixture()
def category() -> Category:
    """Category instance for testing."""
    return Category.objects.create(name="Электроника")


@pytest.fixture()
def another_category() -> Category:
    """Another category for testing."""
    return Category.objects.create(name="Одежда")


@pytest.fixture()
def product(category) -> Product:
    """Product instance for testing."""
    return Product.objects.create(
        name="Смартфон",
        price=Decimal("1000.00"),
        category=category,
        is_promo_excluded=False,
    )


@pytest.fixture()
def expensive_product(category) -> Product:
    """Expensive product instance for testing."""
    return Product.objects.create(
        name="Ноутбук",
        price=Decimal("50000.00"),
        category=category,
        is_promo_excluded=False,
    )


@pytest.fixture()
def promo_excluded_product(category) -> Product:
    """Product that is excluded from promotions, for testing."""
    return Product.objects.create(
        name="Наушники (премиум)",
        price=Decimal("5000.00"),
        category=category,
        is_promo_excluded=True,
    )


@pytest.fixture()
def product_another_category(another_category) -> Product:
    """Product in a different category, for testing category-specific coupons."""
    return Product.objects.create(
        name="Футболка",
        price=Decimal("2000.00"),
        category=another_category,
        is_promo_excluded=False,
    )


@pytest.fixture()
def valid_coupon() -> Coupon:
    """Valid coupon with 10% discount, applicable to all categories."""
    now = timezone.now()
    return Coupon.objects.create(
        code="SALE10",
        discount_percent=Decimal("10.00"),
        valid_from=now - timedelta(days=7),
        valid_until=now + timedelta(days=30),
        max_usages=100,
        usage_count=0,
        category=None,
    )


@pytest.fixture()
def category_coupon(category) -> Coupon:
    """Coupon with 20% discount, applicable only to the 'Электроника' category."""
    now = timezone.now()
    return Coupon.objects.create(
        code="ELECTRONICS20",
        discount_percent=Decimal("20.00"),
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=14),
        max_usages=50,
        usage_count=0,
        category=category,
    )


@pytest.fixture()
def expired_coupon() -> Coupon:
    """Expired coupon with 5% discount, for testing expired coupon scenarios."""
    now = timezone.now()
    return Coupon.objects.create(
        code="EXPIRED5",
        discount_percent=Decimal("5.00"),
        valid_from=now - timedelta(days=60),
        valid_until=now - timedelta(days=1),
        max_usages=10,
        usage_count=0,
        category=None,
    )


@pytest.fixture()
def future_coupon() -> Coupon:
    """Coupon that is not yet valid, for testing future coupon scenarios."""
    now = timezone.now()
    return Coupon.objects.create(
        code="FUTURE50",
        discount_percent=Decimal("50.00"),
        valid_from=now + timedelta(days=10),
        valid_until=now + timedelta(days=40),
        max_usages=10,
        usage_count=0,
        category=None,
    )


@pytest.fixture()
def exhausted_coupon() -> Coupon:
    """Coupon that has reached its maximum usage limit, for testing exhausted coupon scenarios."""
    now = timezone.now()
    return Coupon.objects.create(
        code="MAXED_OUT",
        discount_percent=Decimal("15.00"),
        valid_from=now - timedelta(days=7),
        valid_until=now + timedelta(days=30),
        max_usages=1,
        usage_count=1,
        category=None,
    )


@pytest.fixture()
def full_discount_coupon() -> Coupon:
    """Coupon with 100% discount, for testing edge cases of full discounts."""
    now = timezone.now()
    return Coupon.objects.create(
        code="FREE100",
        discount_percent=Decimal("100.00"),
        valid_from=now - timedelta(days=1),
        valid_until=now + timedelta(days=30),
        max_usages=10,
        usage_count=0,
        category=None,
    )


@pytest.fixture()
def used_coupon_for_user(user, valid_coupon) -> CouponUsage:
    """Creates a CouponUsage instance to simulate that the user has already used the valid_coupon."""
    valid_coupon.usage_count = 1
    valid_coupon.save(update_fields=["usage_count"])
    return CouponUsage.objects.create(user=user, coupon=valid_coupon)
