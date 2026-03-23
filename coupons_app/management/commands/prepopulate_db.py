from django.core.management.base import BaseCommand
from django.db import transaction

from coupons_app.dto import OrderItemData
from coupons_app.tests.data.test_data import (
    CATEGORIES,
    USERS,
    get_coupons,
    get_orders,
    get_products,
)
from coupons_app.models import (
    Category,
    Coupon,
    CouponUsage,
    Order,
    OrderItem,
    Product,
    User,
)
from coupons_app.services import OrderService
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными из coupons_app/tests/data/test_data.py"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить все таблицы приложения перед заполнением.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_db()

        logger.info("Заполнение БД тестовыми данными.")
        users_map = self._create_users()
        categories_map = self._create_categories()
        products_map = self._create_products(categories_map)
        self._create_coupons(categories_map)
        self._create_orders(users_map, products_map)

        logger.info("БД успешно заполнена тестовыми данными.")

    def _clear_db(self):
        """Remove all data from the app's tables."""
        logger.info("Очистка таблиц в БД.")

        OrderItem.objects.all().delete()
        CouponUsage.objects.all().delete()
        Order.objects.all().delete()
        Coupon.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        logger.info("БД успешно очищена.")

    def _create_users(self) -> dict[str, User]:
        """Create users, return {email: User}."""
        result: dict[str, User] = {}
        for data in USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "first_name": data.get("first_name", ""),
                    "last_name": data.get("last_name", ""),
                },
            )
            result[user.email] = user
            status = "создан" if created else "уже существует"
            logger.info("Пользователь %s – %s.", user.email, status)

        return result

    def _create_categories(self) -> dict[str, Category]:
        """Create categories, return {name: Category}."""
        result: dict[str, Category] = {}
        for data in CATEGORIES:
            category, created = Category.objects.get_or_create(name=data["name"])
            result[category.name] = category
            status = "создана" if created else "уже существует"
            logger.info("Категория %s – %s.", category.name, status)

        return result

    def _create_products(
        self, categories_map: dict[str, Category]
    ) -> dict[str, Product]:
        """Create products, return {name: Product}. Expects categories_map for category lookup."""
        result: dict[str, Product] = {}
        for data in get_products():
            category = categories_map[data["category_name"]]
            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "price": data["price"],
                    "category": category,
                    "is_promo_excluded": data.get("is_promo_excluded", False),
                },
            )
            result[product.name] = product
            status = "создан" if created else "уже существует"
            logger.info("Товар %s – %s.", product.name, status)

        return result

    def _create_coupons(self, categories_map: dict[str, Category]) -> None:
        """Create coupons. Expects categories_map for optional category lookup."""
        for data in get_coupons():
            category = (
                categories_map.get(data["category_name"])
                if data.get("category_name")
                else None
            )
            coupon, created = Coupon.objects.get_or_create(
                code=data["code"],
                defaults={
                    "discount_percent": data["discount_percent"],
                    "valid_from": data["valid_from"],
                    "valid_until": data["valid_until"],
                    "max_usages": data["max_usages"],
                    "usage_count": data.get("usage_count", 0),
                    "category": category,
                },
            )
            status = "создан" if created else "уже существует"
            logger.info("Промокод %s – %s.", coupon.code, status)

    def _create_orders(
        self,
        users_map: dict[str, User],
        products_map: dict[str, Product],
    ) -> None:
        """Create orders with items. Expects users_map and products_map for lookups."""
        for idx, data in enumerate(get_orders(), start=1):
            user = users_map.get(data["user_email"])
            if not user:
                logger.info("Пользователь %s не найден, заказ #%s пропущен.", data['user_email'], idx)
                continue

            items_data = []
            skip = False
            for item in data["items"]:
                product = products_map.get(item["product_name"])
                if not product:
                    logger.info("Товар %s не найден, заказ #%s пропущен.", item['product_name'], idx)
                    skip = True
                    break
                items_data.append(
                    OrderItemData(product_id=product.id, quantity=item["quantity"])
                )

            if skip:
                continue

            try:
                order = OrderService.create_order(
                    user_id=user.id,
                    items_data=items_data,
                    coupon_code=data.get("coupon_code"),
                )
                logger.info("Заказ #%s для %s – создан.", order.pk, user.email)
            except Exception as e:
                logger.info("Ошибка при создании заказа #%d: %s", idx, str(e))
