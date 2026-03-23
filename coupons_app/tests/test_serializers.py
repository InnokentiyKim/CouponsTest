from datetime import timedelta

import pytest
from django.utils import timezone

from coupons_app.serializers import (
    CategoryInputSerializer,
    CouponInputSerializer,
    CreateOrderSerializer,
    OrderItemInputSerializer,
    ProductInputSerializer,
    UserInputSerializer,
)


class TestCreateOrderSerializer:
    """Tests for CreateOrderSerializer validation logic."""
    def test_valid_input(self):
        """Test that valid input data passes validation."""
        data = {
            "user_id": 1,
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1},
            ],
        }
        serializer = CreateOrderSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_valid_input_with_coupon(self):
        """Test that valid input with a coupon code passes validation."""
        data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
            "coupon_code": "SALE10",
        }
        serializer = CreateOrderSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_empty_items_raises(self):
        """Test that an empty items list raises a validation error."""
        data = {"user_id": 1, "items": []}
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "items" in serializer.errors

    def test_duplicate_product_ids_raises(self):
        """Test that duplicate product_ids in items raise a validation error."""
        data = {
            "user_id": 1,
            "items": [
                {"product_id": 1, "quantity": 1},
                {"product_id": 1, "quantity": 2},
            ],
        }
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "items" in serializer.errors

    def test_missing_user_id_raises(self):
        """Test that missing user_id raises a validation error."""
        data = {"items": [{"product_id": 1, "quantity": 1}]}
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "user_id" in serializer.errors

    def test_quantity_zero_raises(self):
        """Test that a quantity of zero in items raises a validation error."""
        data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 0}],
        }
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "items" in serializer.errors

    def test_negative_user_id_raises(self):
        """Test that a negative user_id raises a validation error."""
        data = {
            "user_id": -1,
            "items": [{"product_id": 1, "quantity": 1}],
        }
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "user_id" in serializer.errors

    def test_negative_product_id_raises(self):
        """Test that a negative product_id in items raises a validation error."""
        data = {
            "user_id": 1,
            "items": [{"product_id": -5, "quantity": 1}],
        }
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "items" in serializer.errors

    def test_missing_items_raises(self):
        """Test that missing items field raises a validation error."""
        data = {"user_id": 1}
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "items" in serializer.errors

    def test_blank_coupon_code_raises(self):
        """Test that a blank coupon_code raises a validation error."""
        data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 1}],
            "coupon_code": "",
        }
        serializer = CreateOrderSerializer(data=data)
        assert not serializer.is_valid()
        assert "coupon_code" in serializer.errors


@pytest.mark.django_db
class TestCouponInputSerializer:
    """Tests for CouponInputSerializer validation logic, including date validation and discount percentage limits."""
    def test_valid_coupon_data(self):
        """Test that valid coupon data passes validation."""
        now = timezone.now()
        data = {
            "code": "TEST10",
            "discount_percent": "10.00",
            "valid_from": (now - timedelta(days=1)).isoformat(),
            "valid_until": (now + timedelta(days=30)).isoformat(),
            "max_usages": 50,
        }
        serializer = CouponInputSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_dates_raises(self):
        """Test that valid_until date before valid_from raises a validation error."""
        now = timezone.now()
        data = {
            "code": "BADDATE",
            "discount_percent": "10.00",
            "valid_from": (now + timedelta(days=10)).isoformat(),
            "valid_until": (now - timedelta(days=1)).isoformat(),
            "max_usages": 5,
        }
        serializer = CouponInputSerializer(data=data)
        assert not serializer.is_valid()

    def test_discount_over_100_raises(self):
        """Test that a discount_percent value over 100 raises a validation error."""
        now = timezone.now()
        data = {
            "code": "OVER100",
            "discount_percent": "150.00",
            "valid_from": (now - timedelta(days=1)).isoformat(),
            "valid_until": (now + timedelta(days=30)).isoformat(),
            "max_usages": 10,
        }
        serializer = CouponInputSerializer(data=data)
        assert not serializer.is_valid()

    def test_missing_code_raises(self):
        """Test that missing code field raises a validation error."""
        now = timezone.now()
        data = {
            "discount_percent": "10.00",
            "valid_from": (now - timedelta(days=1)).isoformat(),
            "valid_until": (now + timedelta(days=30)).isoformat(),
            "max_usages": 10,
        }
        serializer = CouponInputSerializer(data=data)
        assert not serializer.is_valid()
        assert "code" in serializer.errors


class TestOrderItemInputSerializer:
    """Tests for OrderItemInputSerializer validation logic, ensuring that both product_id and quantity are required and valid."""
    def test_valid(self):
        """Test that valid product_id and quantity pass validation."""
        serializer = OrderItemInputSerializer(data={"product_id": 1, "quantity": 3})
        assert serializer.is_valid()

    def test_missing_product_id(self):
        """Test that missing product_id raises a validation error."""
        serializer = OrderItemInputSerializer(data={"quantity": 1})
        assert not serializer.is_valid()
        assert "product_id" in serializer.errors

    def test_missing_quantity(self):
        """Test that missing quantity raises a validation error."""
        serializer = OrderItemInputSerializer(data={"product_id": 1})
        assert not serializer.is_valid()
        assert "quantity" in serializer.errors


@pytest.mark.django_db
class TestUserInputSerializer:
    """Tests for UserInputSerializer validation logic, ensuring that email is required and properly formatted."""
    def test_valid(self):
        """Test that valid email and optional first_name and last_name pass validation."""
        data = {
            "email": "test@example.com",
            "first_name": "Тест",
            "last_name": "Тестов",
        }
        serializer = UserInputSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_email_required(self):
        """Test that missing email raises a validation error."""
        serializer = UserInputSerializer(data={"first_name": "Тест"})
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_invalid_email(self):
        """Test that an invalid email format raises a validation error."""
        serializer = UserInputSerializer(data={"email": "not-an-email"})
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestCategoryInputSerializer:
    """Tests for CategoryInputSerializer validation logic, ensuring that name is required."""
    def test_valid(self):
        """Test that a valid name passes validation."""
        serializer = CategoryInputSerializer(data={"name": "Книги"})
        assert serializer.is_valid()

    def test_name_required(self):
        """Test that missing name raises a validation error."""
        serializer = CategoryInputSerializer(data={})
        assert not serializer.is_valid()
        assert "name" in serializer.errors


@pytest.mark.django_db
class TestProductInputSerializer:
    """Tests for ProductInputSerializer validation logic, ensuring that name, price, and category are required and valid."""
    def test_valid(self, category):
        """Test that valid name, price, and category pass validation."""
        data = {
            "name": "Товар",
            "price": "500.00",
            "category": category.id,
        }
        serializer = ProductInputSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_missing_price(self, category):
        """Test that missing price raises a validation error."""
        data = {"name": "Товар", "category": category.id}
        serializer = ProductInputSerializer(data=data)
        assert not serializer.is_valid()
        assert "price" in serializer.errors

    def test_missing_category(self):
        """Test that missing category raises a validation error."""
        data = {"name": "Товар", "price": "500.00"}
        serializer = ProductInputSerializer(data=data)
        assert not serializer.is_valid()
        assert "category" in serializer.errors
