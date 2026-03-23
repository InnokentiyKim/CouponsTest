from datetime import timedelta

from django.utils import timezone


USERS = [
    {
        "email": "ivan@example.com",
        "first_name": "Иван",
        "last_name": "Петров",
    },
    {
        "email": "anna@example.com",
        "first_name": "Анна",
        "last_name": "Сидорова",
    },
    {
        "email": "guest@example.com",
        "first_name": "",
        "last_name": "",
    },
]


CATEGORIES = [
    {"name": "Электроника"},
    {"name": "Одежда"},
    {"name": "Книги"},
]


def get_products() -> list[dict]:
    """Returns list of products."""
    return [
        {
            "name": "Смартфон",
            "price": "29999.99",
            "category_name": "Электроника",
            "is_promo_excluded": False,
        },
        {
            "name": "Ноутбук",
            "price": "89999.00",
            "category_name": "Электроника",
            "is_promo_excluded": False,
        },
        {
            "name": "Наушники (премиум)",
            "price": "14999.50",
            "category_name": "Электроника",
            "is_promo_excluded": True,
        },
        {
            "name": "Футболка",
            "price": "1999.00",
            "category_name": "Одежда",
            "is_promo_excluded": False,
        },
        {
            "name": "Куртка",
            "price": "12500.00",
            "category_name": "Одежда",
            "is_promo_excluded": False,
        },
        {
            "name": "Роман «Война и мир»",
            "price": "750.00",
            "category_name": "Книги",
            "is_promo_excluded": False,
        },
    ]


def get_coupons() -> list[dict]:
    """Returns list of coupons."""
    now = timezone.now()
    return [
        {
            "code": "SALE10",
            "discount_percent": "10.00",
            "valid_from": now - timedelta(days=7),
            "valid_until": now + timedelta(days=30),
            "max_usages": 100,
            "category_name": None,
        },
        {
            "code": "ELECTRONICS20",
            "discount_percent": "20.00",
            "valid_from": now - timedelta(days=1),
            "valid_until": now + timedelta(days=14),
            "max_usages": 50,
            "category_name": "Электроника",
        },
        {
            "code": "EXPIRED5",
            "discount_percent": "5.00",
            "valid_from": now - timedelta(days=60),
            "valid_until": now - timedelta(days=1),
            "max_usages": 10,
            "category_name": None,
        },
        {
            "code": "MAXED_OUT",
            "discount_percent": "15.00",
            "valid_from": now - timedelta(days=7),
            "valid_until": now + timedelta(days=30),
            "max_usages": 1,
            "usage_count": 1,
            "category_name": None,
        },
        {
            "code": "HALF_PRICE",
            "discount_percent": "50.00",
            "valid_from": now - timedelta(days=3),
            "valid_until": now + timedelta(days=60),
            "max_usages": 200,
            "category_name": None,
        },
    ]


def get_orders() -> list[dict]:
    """Returns list of orders."""
    return [
        {
            "user_email": "ivan@example.com",
            "coupon_code": "SALE10",
            "items": [
                {"product_name": "Смартфон", "quantity": 1},
                {"product_name": "Футболка", "quantity": 2},
            ],
        },
        {
            "user_email": "anna@example.com",
            "coupon_code": None,
            "items": [
                {"product_name": "Роман «Война и мир»", "quantity": 3},
            ],
        },
        {
            "user_email": "anna@example.com",
            "coupon_code": "ELECTRONICS20",
            "items": [
                {"product_name": "Ноутбук", "quantity": 1},
                {"product_name": "Наушники (премиум)", "quantity": 1},
            ],
        },
    ]
