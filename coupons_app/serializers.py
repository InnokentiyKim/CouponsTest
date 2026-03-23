from rest_framework import serializers

from coupons_app.models import Category, Coupon, Order, OrderItem, Product, User


class UserInputSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a user."""

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]


class UserOutputSerializer(serializers.ModelSerializer):
    """Serializer for user representation in responses."""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "created_at"]
        read_only_fields = fields


class CategoryInputSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a category."""

    class Meta:
        model = Category
        fields = ["name"]


class CategoryOutputSerializer(serializers.ModelSerializer):
    """Serializer for category representation in responses."""

    class Meta:
        model = Category
        fields = ["id", "name"]
        read_only_fields = fields


class ProductInputSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a product."""

    class Meta:
        model = Product
        fields = ["name", "price", "category", "is_promo_excluded"]


class ProductOutputSerializer(serializers.ModelSerializer):
    """Serializer for product representation in responses."""

    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "category",
            "category_name",
            "is_promo_excluded",
        ]
        read_only_fields = fields


class CouponInputSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a coupon. Validates through model's clean() method."""

    class Meta:
        model = Coupon
        fields = [
            "code",
            "discount_percent",
            "valid_from",
            "valid_until",
            "max_usages",
            "category",
        ]

    def validate(self, attrs: dict) -> dict:
        """Performs object-level validation by creating a temporary Coupon instance and calling its clean() method."""
        instance = Coupon(**attrs)
        instance.clean()
        return attrs


class CouponOutputSerializer(serializers.ModelSerializer):
    """Serializer for coupon representation in responses."""

    category_name = serializers.CharField(
        source="category.name",
        default=None,
        read_only=True,
    )

    class Meta:
        model = Coupon
        fields = [
            "id",
            "code",
            "discount_percent",
            "valid_from",
            "valid_until",
            "max_usages",
            "usage_count",
            "category",
            "category_name",
        ]
        read_only_fields = fields


class OrderItemInputSerializer(serializers.Serializer):
    """Serializer for a single order item in the order creation request."""

    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order. Validates that items list is not empty and has no duplicate product_ids."""

    user_id = serializers.IntegerField(min_value=1)
    items = OrderItemInputSerializer(many=True)
    coupon_code = serializers.CharField(
        max_length=64,
        required=False,
        allow_blank=False,
    )

    def validate_items(self, value: list[dict]) -> list[dict]:
        """Checks that the items list is not empty and does not contain duplicate product_ids."""
        if not value:
            raise serializers.ValidationError(
                "Заказ должен содержать хотя бы одну позицию."
            )

        product_ids = [item["product_id"] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                "Список позиций содержит дублирующиеся товары."
            )

        return value


class OrderItemOutputSerializer(serializers.ModelSerializer):
    """Serializer for a single order item in the order representation."""

    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "product_id",
            "product_name",
            "quantity",
            "price_per_item",
            "discount_amount",
        ]


class OrderOutputSerializer(serializers.ModelSerializer):
    """Serializer for order representation in responses. Includes nested items and coupon code."""

    items = OrderItemOutputSerializer(many=True, read_only=True)
    coupon_code = serializers.CharField(
        source="coupon.code",
        default=None,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "user_id",
            "items",
            "original_total",
            "discounted_total",
            "coupon_code",
            "created_at",
        ]
        read_only_fields = fields
