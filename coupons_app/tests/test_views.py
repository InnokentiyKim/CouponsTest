from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from coupons_app.models import Category, Coupon, Order, Product, User


@pytest.mark.django_db
class TestUserViews:
    """Tests for User API endpoints."""
    def test_list_users(self, api_client, user):
        """Check that the user list endpoint returns users."""
        resp = api_client.get("/api/v1/users/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_create_user(self, api_client):
        """Check that we can create a new user via the API."""
        resp = api_client.post(
            "/api/v1/users/",
            {"email": "new@example.com", "first_name": "Новый"},
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["email"] == "new@example.com"

    def test_get_user_detail(self, api_client, user):
        """Check that we can retrieve a user's details by ID."""
        resp = api_client.get(f"/api/v1/users/{user.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == user.id

    def test_update_user(self, api_client, user):
        """Check that we can update a user's email via the API."""
        resp = api_client.put(
            f"/api/v1/users/{user.id}/",
            {"email": "updated@example.com"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == "updated@example.com"

    def test_delete_user(self, api_client, user):
        """Check that we can delete a user via the API."""
        resp = api_client.delete(f"/api/v1/users/{user.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=user.id).exists()

    def test_get_nonexistent_user(self, api_client, db):
        """Check that requesting a non-existent user returns 404."""
        resp = api_client.get("/api/v1/users/99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCategoryViews:
    """Tests for Category API endpoints."""
    def test_list_categories(self, api_client, category):
        """Check that the category list endpoint returns categories."""
        resp = api_client.get("/api/v1/categories/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_create_category(self, api_client):
        """Check that we can create a new category via the API."""
        resp = api_client.post(
            "/api/v1/categories/",
            {"name": "Игрушки"},
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["name"] == "Игрушки"

    def test_get_category_detail(self, api_client, category):
        """Check that we can retrieve a category's details by ID."""
        resp = api_client.get(f"/api/v1/categories/{category.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == category.id

    def test_update_category(self, api_client, category):
        """Check that we can update a category's name via the API."""
        resp = api_client.put(
            f"/api/v1/categories/{category.id}/",
            {"name": "Бытовая техника"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == "Бытовая техника"

    def test_delete_category(self, api_client, category):
        """Check that we can delete a category via the API."""
        resp = api_client.delete(f"/api/v1/categories/{category.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=category.id).exists()

    def test_get_nonexistent_category(self, api_client, db):
        """Check that requesting a non-existent category returns 404."""
        resp = api_client.get("/api/v1/categories/99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestProductViews:
    """Tests for Product API endpoints."""
    def test_list_products(self, api_client, product):
        """Check that the product list endpoint returns products."""
        resp = api_client.get("/api/v1/products/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_create_product(self, api_client, category):
        """Check that we can create a new product via the API."""
        resp = api_client.post(
            "/api/v1/products/",
            {
                "name": "Планшет",
                "price": "15000.00",
                "category": category.id,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["name"] == "Планшет"

    def test_get_product_detail(self, api_client, product):
        """Check that we can retrieve a product's details by ID."""
        resp = api_client.get(f"/api/v1/products/{product.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == product.id

    def test_update_product(self, api_client, product):
        """Check that we can update a product's name via the API."""
        resp = api_client.put(
            f"/api/v1/products/{product.id}/",
            {"name": "Смартфон Pro"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.name == "Смартфон Pro"

    def test_delete_product(self, api_client, product):
        """Check that we can delete a product via the API."""
        resp = api_client.delete(f"/api/v1/products/{product.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(pk=product.id).exists()

    def test_get_nonexistent_product(self, api_client, db):
        """Check that requesting a non-existent product returns 404."""
        resp = api_client.get("/api/v1/products/99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCouponViews:
    """Tests for Coupon API endpoints."""
    def test_list_coupons(self, api_client, valid_coupon):
        """Check that the coupon list endpoint returns coupons."""
        resp = api_client.get("/api/v1/coupons/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_create_coupon(self, api_client):
        """Check that we can create a new coupon via the API with valid data."""
        now = timezone.now()
        resp = api_client.post(
            "/api/v1/coupons/",
            {
                "code": "NEWCOUPON",
                "discount_percent": "25.00",
                "valid_from": (now - timedelta(days=1)).isoformat(),
                "valid_until": (now + timedelta(days=30)).isoformat(),
                "max_usages": 100,
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["code"] == "NEWCOUPON"

    def test_get_coupon_detail(self, api_client, valid_coupon):
        """Check that we can retrieve a coupon's details by ID."""
        resp = api_client.get(f"/api/v1/coupons/{valid_coupon.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == valid_coupon.id

    def test_delete_coupon(self, api_client, valid_coupon):
        """Check that we can delete a coupon via the API."""
        resp = api_client.delete(f"/api/v1/coupons/{valid_coupon.id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Coupon.objects.filter(pk=valid_coupon.id).exists()

    def test_get_nonexistent_coupon(self, api_client, db):
        """Check that requesting a non-existent coupon returns 404."""
        resp = api_client.get("/api/v1/coupons/99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestOrderViews:
    """Tests for Order API endpoints."""
    def test_create_order_via_api(self, api_client, user, product):
        """Check that we can create an order via the API without a coupon."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 2}],
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["original_total"] == "2000.00"
        assert resp.data["discounted_total"] == "2000.00"
        assert len(resp.data["items"]) == 1

    def test_create_order_with_coupon_via_api(
        self, api_client, user, product, valid_coupon
    ):
        """Check that we can create an order with a valid coupon via the API."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 1}],
                "coupon_code": "SALE10",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["discounted_total"] == "900.00"
        assert resp.data["coupon_code"] == "SALE10"

    def test_create_order_invalid_coupon_via_api(self, api_client, user, product):
        """Check that creating an order with an invalid coupon code returns an error."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 1}],
                "coupon_code": "FAKE_CODE",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_list_orders(self, api_client, user, product):
        """Check that the order list endpoint returns orders for the user."""
        api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 1}],
            },
            format="json",
        )
        resp = api_client.get("/api/v1/orders/")
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) >= 1

    def test_get_order_detail(self, api_client, user, product):
        """Check that we can retrieve an order's details by ID."""
        create_resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 1}],
            },
            format="json",
        )
        order_id = create_resp.data["id"]
        resp = api_client.get(f"/api/v1/orders/{order_id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == order_id

    def test_delete_order(self, api_client, user, product):
        """Check that we can delete an order via the API."""
        create_resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 1}],
            },
            format="json",
        )
        order_id = create_resp.data["id"]
        resp = api_client.delete(f"/api/v1/orders/{order_id}/")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        assert not Order.objects.filter(pk=order_id).exists()

    def test_get_nonexistent_order(self, api_client, db):
        """Check that requesting a non-existent order returns 404."""
        resp = api_client.get("/api/v1/orders/99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_create_order_empty_items_via_api(self, api_client, user):
        """Check that creating an order with an empty items list returns an error."""
        resp = api_client.post(
            "/api/v1/orders/",
            {"user_id": user.id, "items": []},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_nonexistent_user_via_api(self, api_client, product):
        """Check that creating an order with a non-existent user ID returns an error."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": 99999,
                "items": [{"product_id": product.id, "quantity": 1}],
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_create_order_nonexistent_product_via_api(self, api_client, user):
        """Check that creating an order with a non-existent product ID in items returns an error."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": 99999, "quantity": 1}],
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_expired_coupon_via_api(
        self, api_client, user, product, expired_coupon
    ):
        """Check that creating an order with an expired coupon code returns an error."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [{"product_id": product.id, "quantity": 1}],
                "coupon_code": "EXPIRED5",
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_order_duplicate_product_ids_via_api(
        self, api_client, user, product
    ):
        """Check that creating an order with duplicate product IDs in items returns an error."""
        resp = api_client.post(
            "/api/v1/orders/",
            {
                "user_id": user.id,
                "items": [
                    {"product_id": product.id, "quantity": 1},
                    {"product_id": product.id, "quantity": 2},
                ],
            },
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
