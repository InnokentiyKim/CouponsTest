from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class User(models.Model):
    """User of the system, identified by a unique email address."""

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Фамилия",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации",
    )

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.email

    def clean(self) -> None:
        """Normalize and validate email."""
        super().clean()
        if not self.email or not self.email.strip():
            raise ValidationError({"email": "Email не может быть пустым."})
        self.email = self.email.strip().lower()

    def save(self, *args, **kwargs):
        """Ensure full_clean is called before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class Category(models.Model):
    """Product category, which can be used to group products and restrict coupon applicability."""

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Normalize and validate category name."""
        super().clean()
        if not self.name or not self.name.strip():
            raise ValidationError({"name": "Название категории не может быть пустым."})
        self.name = self.name.strip()

    def save(self, *args, **kwargs) -> None:
        """Ensure full_clean is called before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product that can be ordered and may be eligible for coupons."""

    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Цена",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория",
    )
    is_promo_excluded = models.BooleanField(
        default=False,
        verbose_name="Исключён из акций",
        help_text="Если True, промокоды к этому товару не применяются.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.price}₽)"

    def clean(self) -> None:
        """Validate that price is positive."""
        super().clean()
        if self.price is not None and self.price <= 0:
            raise ValidationError({"price": "Цена товара должна быть больше нуля."})

    def save(self, *args, **kwargs):
        """Ensure full_clean is called before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """Coupon that can be applied to orders for discounts. May have usage limits and category restrictions."""

    code = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Код промокода",
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("100.00")),
        ],
        verbose_name="Скидка (%)",
    )
    valid_from = models.DateTimeField(verbose_name="Действителен с")
    valid_until = models.DateTimeField(
        db_index=True,
        verbose_name="Действителен до",
    )
    max_usages = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Макс. кол-во использований",
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Текущее кол-во использований",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coupons",
        verbose_name="Ограничение по категории",
        help_text="Если указано, промокод действует только на товары этой категории.",
    )

    class Meta:
        ordering = ["-valid_until"]

    def __str__(self) -> str:
        return f"{self.code} (-{self.discount_percent}%)"

    def clean(self) -> None:
        """Validate coupon fields for logical consistency and value ranges."""
        super().clean()
        errors: dict[str, str] = {}

        if self.discount_percent is not None and not (
            Decimal("0.01") <= self.discount_percent <= Decimal("100.00")
        ):
            errors["discount_percent"] = "Скидка должна быть от 0.01% до 100%."

        if self.max_usages is not None and self.max_usages < 1:
            errors["max_usages"] = "Максимальное кол-во использований должно быть ≥ 1."

        if self.valid_from and self.valid_until and self.valid_from >= self.valid_until:
            errors["valid_until"] = "Дата окончания должна быть позже даты начала."

        if errors:
            raise ValidationError(errors)

    def is_valid_at(self, dt: timezone.datetime | None = None) -> bool:
        """Check if the coupon is currently valid based on the provided datetime (or now if not provided)."""
        dt = dt or timezone.now()
        return self.valid_from <= dt <= self.valid_until

    def save(self, *args, **kwargs):
        """Ensure full_clean is called before saving to enforce validation."""
        self.full_clean()
        super().save(*args, **kwargs)


class Order(models.Model):
    """Order placed by a user, which may have an applied coupon and contains multiple order items."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Применённый промокод",
    )
    original_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма без скидки",
    )
    discounted_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма со скидкой",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Заказ #{self.pk} (пользователь {self.user_id})"


class OrderItem(models.Model):
    """OrderItem represents a specific product and quantity within an Order, along with pricing details."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество",
    )
    price_per_item = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена за единицу",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Сумма скидки",
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity}"

    def clean(self) -> None:
        """Validate that quantity is at least 1 and that price fields are non-negative."""
        super().clean()
        if self.quantity is not None and self.quantity < 1:
            raise ValidationError({"quantity": "Количество должно быть ≥ 1."})

    def save(self, *args, **kwargs):
        """Ensure full_clean is called before saving to enforce validation."""
        self.full_clean()
        super().save(*args, **kwargs)


class CouponUsage(models.Model):
    """CouponUsage tracks each instance of a coupon being used by a user, enforcing unique usage per user-coupon pair."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
        verbose_name="Пользователь",
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages",
        verbose_name="Промокод",
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата использования",
    )

    class Meta:
        verbose_name = "Использование промокода"
        verbose_name_plural = "Использования промокодов"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "coupon"],
                name="unique_user_coupon_usage",
            ),
        ]

    def __str__(self) -> str:
        return f"Пользователь {self.user_id} -> {self.coupon.code}"
