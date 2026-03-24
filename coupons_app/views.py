from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from coupons_app.dto import OrderItemData
from rest import errocodes as errors
from coupons_app.models import Category, Coupon, Order, Product, User
from coupons_app.serializers import (
    CategoryInputSerializer,
    CategoryOutputSerializer,
    CouponInputSerializer,
    CouponOutputSerializer,
    CreateOrderSerializer,
    OrderOutputSerializer,
    ProductInputSerializer,
    ProductOutputSerializer,
    UserInputSerializer,
    UserOutputSerializer,
)
from coupons_app.services import OrderService


class UserListCreateView(APIView):
    """View for listing all users and creating a new user."""

    def get(self, request: Request) -> Response:
        """List all users."""
        users = User.objects.all()
        serializer = UserOutputSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new user."""
        serializer = UserInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        output = UserOutputSerializer(user)
        return Response(output.data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    """View for retrieving, updating, and deleting a user by ID."""

    @staticmethod
    def _get_user(pk: int) -> User:
        """Helper method to retrieve a user by ID or raise NotFound."""
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise errors.ItemNotFoundException(detail=f"Пользователь с id={pk} не найден.", code="User not found")

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve a user by ID."""
        user = self._get_user(pk)
        serializer = UserOutputSerializer(user)
        return Response(serializer.data)

    def put(self, request: Request, pk: int) -> Response:
        """Update a user by ID."""
        user = self._get_user(pk)
        serializer = UserInputSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output = UserOutputSerializer(user)
        return Response(output.data)

    def delete(self, request: Request, pk: int) -> Response:
        """Delete a user by ID."""
        user = self._get_user(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateView(APIView):
    """View for listing all categories and creating a new category."""

    def get(self, request: Request) -> Response:
        """List all categories."""
        categories = Category.objects.all()
        serializer = CategoryOutputSerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new category."""
        serializer = CategoryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        output = CategoryOutputSerializer(category)
        return Response(output.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    """View for retrieving, updating, and deleting a category by ID."""

    @staticmethod
    def _get_category(pk: int) -> Category:
        """Helper method to retrieve a category by ID or raise NotFound."""
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise errors.ItemNotFoundException(detail=f"Категория с id={pk} не найдена.", code="Category not found")

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve a category by ID."""
        category = self._get_category(pk)
        serializer = CategoryOutputSerializer(category)
        return Response(serializer.data)

    def put(self, request: Request, pk: int) -> Response:
        """Update a category by ID."""
        category = self._get_category(pk)
        serializer = CategoryInputSerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output = CategoryOutputSerializer(category)
        return Response(output.data)

    def delete(self, request: Request, pk: int) -> Response:
        """Delete a category by ID."""
        category = self._get_category(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListCreateView(APIView):
    """View for listing all products and creating a new product."""

    def get(self, request: Request) -> Response:
        """List all products."""
        products = Product.objects.select_related("category").all()
        serializer = ProductOutputSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new product."""
        serializer = ProductInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        output = ProductOutputSerializer(product)
        return Response(output.data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    """View for retrieving, updating, and deleting a product by ID."""

    @staticmethod
    def _get_product(pk: int) -> Product:
        """Helper method to retrieve a product by ID or raise NotFound. Uses select_related for category."""
        try:
            return Product.objects.select_related("category").get(pk=pk)
        except Product.DoesNotExist:
            raise errors.ItemNotFoundException(detail=f"Товар с id={pk} не найден.", code="Product not found")

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve a product by ID."""
        product = self._get_product(pk)
        serializer = ProductOutputSerializer(product)
        return Response(serializer.data)

    def put(self, request: Request, pk: int) -> Response:
        """Update a product by ID."""
        product = self._get_product(pk)
        serializer = ProductInputSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        product.refresh_from_db()
        output = ProductOutputSerializer(
            Product.objects.select_related("category").get(pk=pk)
        )
        return Response(output.data)

    def delete(self, request: Request, pk: int) -> Response:
        """Delete a product by ID."""
        product = self._get_product(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CouponListCreateView(APIView):
    """View for listing all coupons and creating a new coupon."""

    def get(self, request: Request) -> Response:
        """List all coupons."""
        coupons = Coupon.objects.select_related("category").all()
        serializer = CouponOutputSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new coupon."""
        serializer = CouponInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        coupon = serializer.save()
        output = CouponOutputSerializer(coupon)
        return Response(output.data, status=status.HTTP_201_CREATED)


class CouponDetailView(APIView):
    """View for retrieving, updating, and deleting a coupon by ID."""

    @staticmethod
    def _get_coupon(pk: int) -> Coupon:
        """Helper method to retrieve a coupon by ID or raise NotFound. Uses select_related for category."""
        try:
            return Coupon.objects.select_related("category").get(pk=pk)
        except Coupon.DoesNotExist:
            raise errors.ItemNotFoundException(detail=f"Промокод с id={pk} не найден.", code="Coupon not found")

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve a coupon by ID."""
        coupon = self._get_coupon(pk)
        serializer = CouponOutputSerializer(coupon)
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        """Delete a coupon by ID."""
        coupon = self._get_coupon(pk)
        coupon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListCreateView(APIView):
    """View for listing all orders and creating a new order. Uses OrderService for order creation logic."""

    def get(self, request: Request) -> Response:
        """List all orders with related items, products, and coupons to minimize queries."""
        orders = (
            Order.objects.prefetch_related("items__product")
            .select_related("coupon")
            .all()
        )
        serializer = OrderOutputSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        """Create a new order."""
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        data_items = data["items"]
        order_items: list[OrderItemData] = [
            OrderItemData(product_id=item["product_id"], quantity=item["quantity"])
            for item in data_items
        ]
        order = OrderService.create_order(
            user_id=data["user_id"],
            items_data=order_items,
            coupon_code=data.get("coupon_code"),
        )

        output = OrderOutputSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    """View for retrieving and deleting an order by ID. Uses select_related and prefetch_related to optimize queries."""

    @staticmethod
    def _get_order(pk: int) -> Order:
        """Helper method to retrieve an order by ID or raise NotFound."""
        try:
            return (
                Order.objects.prefetch_related("items__product")
                .select_related("coupon")
                .get(pk=pk)
            )
        except Order.DoesNotExist:
            raise errors.ItemNotFoundException(detail=f"Заказ с id={pk} не найден.", code="Order not found")

    def get(self, request: Request, pk: int) -> Response:
        """Retrieve an order by ID."""
        order = self._get_order(pk)
        serializer = OrderOutputSerializer(order)
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        """Delete an order by ID."""
        order = self._get_order(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
