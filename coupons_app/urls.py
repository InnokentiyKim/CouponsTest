from django.urls import path

from coupons_app.views import (
    CategoryDetailView,
    CategoryListCreateView,
    CouponDetailView,
    CouponListCreateView,
    OrderDetailView,
    OrderListCreateView,
    ProductDetailView,
    ProductListCreateView,
    UserDetailView,
    UserListCreateView,
)

app_name = "coupons_app"

urlpatterns = [
    # Users
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    # Products
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    # Coupons
    path("coupons/", CouponListCreateView.as_view(), name="coupon-list-create"),
    path("coupons/<int:pk>/", CouponDetailView.as_view(), name="coupon-detail"),
    # Orders
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
