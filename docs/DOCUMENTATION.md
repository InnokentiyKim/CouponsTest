# Coupons API

REST API для управления пользователями, товарами, категориями, промокодами и заказами.

**Базовый URL:** `http://localhost:8000/api/v1`

---

## Содержание

- [Users — Пользователи](#users--пользователи)
- [Categories — Категории](#categories--категории)
- [Products — Товары](#products--товары)
- [Coupons — Промокоды](#coupons--промокоды)
- [Orders — Заказы](#orders--заказы)
- [Коды ошибок](#коды-ошибок)

---

## Users — Пользователи

### `GET /api/v1/users/`

Возвращает список всех пользователей.

**Пример запроса:**
```
GET /api/v1/users/
```

---

### `POST /api/v1/users/`

Создаёт нового пользователя.

**Тело запроса:**

`email` — единственное обязательное поле. 
`first_name` и `last_name` — опциональные.

**Пример запроса:**
```json
POST /api/v1/users/
Content-Type: application/json

{
  "email": "guest@example.com",
  "first_name": "Гость",
  "last_name": ""
}
```

---

### `GET /api/v1/users/{id}/`

Возвращает пользователя по ID.

**Пример запроса:**
```
GET /api/v1/users/1/
```

---

### `PUT /api/v1/users/{id}/`

Обновляет данные пользователя по ID.

**Пример запроса:**
```json
PUT /api/v1/users/1/
Content-Type: application/json

{
  "first_name": "Иван",
  "last_name": "Новиков"
}
```

---

### `DELETE /api/v1/users/{id}/`

Удаляет пользователя по ID.

**Пример запроса:**
```
DELETE /api/v1/users/1/
```

---

## Categories — Категории

### `GET /api/v1/categories/`

Возвращает список всех категорий.

---

### `POST /api/v1/categories/`

Создаёт новую категорию.

**Тело запроса:**

`name` — единственное обязательное поле, должно быть уникальным.

**Пример запроса:**
```json
POST /api/v1/categories/
Content-Type: application/json

{
  "name": "Спорт"
}
```

---

### `GET /api/v1/categories/{id}/`

Возвращает категорию по ID.

---

### `PUT /api/v1/categories/{id}/`

Обновляет категорию по ID.

**Пример запроса:**
```json
PUT /api/v1/categories/1/
Content-Type: application/json

{
  "name": "Электроника и гаджеты"
}
```

---

### `DELETE /api/v1/categories/{id}/`

Удаляет категорию по ID.

---

## Products — Товары

### `GET /api/v1/products/`

Возвращает список всех товаров с информацией о категории.

---

### `POST /api/v1/products/`

Создаёт новый товар.

**Тело запроса:**

`name`, `price` и `category_id` — обязательные поля.
`is_promo_excluded` — опциональное, по умолчанию `false`.

**Пример запроса:**
```json
POST /api/v1/products/
Content-Type: application/json

{
  "name": "Планшет",
  "price": "45000.00",
  "category_id": 1,
  "is_promo_excluded": false
}
```

---

### `GET /api/v1/products/{id}/`

Возвращает товар по ID.

---

### `PUT /api/v1/products/{id}/`

Обновляет товар по ID.

**Пример запроса:**
```json
PUT /api/v1/products/1/
Content-Type: application/json

{
  "price": "27999.99"
}
```

---

### `DELETE /api/v1/products/{id}/`

Удаляет товар по ID.

---

## Coupons — Промокоды

### `GET /api/v1/coupons/`

Возвращает список всех промокодов.

---

### `POST /api/v1/coupons/`

Создаёт новый промокод.

**Тело запроса:**

`code`, `discount_percent`, `valid_from`, `valid_until` и `max_usages` — обязательные поля.
`category_id` — опциональное, если скидка только на определённую категорию

**Пример запроса:**
```json
POST /api/v1/coupons/
Content-Type: application/json

{
  "code": "SUMMER25",
  "discount_percent": "25.00",
  "valid_from": "2025-06-01T00:00:00Z",
  "valid_until": "2025-08-31T23:59:59Z",
  "max_usages": 500,
  "category_id": null
}
```

---

### `GET /api/v1/coupons/{id}/`

Возвращает промокод по ID.

---

### `PUT /api/v1/coupons/{id}/`

Обновляет промокод по ID.

**Пример запроса:**
```json
PUT /api/v1/coupons/1/
Content-Type: application/json

{
  "max_usages": 200
}
```

---

### `DELETE /api/v1/coupons/{id}/`

Удаляет промокод по ID.

---

## Orders — Заказы

### `GET /api/v1/orders/`

Возвращает список всех заказов с позициями и применённым промокодом.

---

### `POST /api/v1/orders/`

Создаёт новый заказ. Автоматически рассчитывает итоговые суммы с учётом промокода.

**Тело запроса:**

`user_id` и `items` — обязательные поля. `coupon_code` — опциональное.
`items` — массив объектов, каждый с `product_id` и `quantity`.

**Пример запроса без промокода:**
```json
POST /api/v1/orders/
Content-Type: application/json

{
  "user_id": 2,
  "items": [
    { "product_id": 6, "quantity": 3 }
  ]
}
```

**Пример запроса с промокодом:**
```json
POST /api/v1/orders/
Content-Type: application/json

{
  "user_id": 1,
  "items": [
    { "product_id": 1, "quantity": 1 },
    { "product_id": 4, "quantity": 2 }
  ],
  "coupon_code": "SALE10"
}
```

> **Примечание:** Товары с `is_promo_excluded: true` не получают скидку даже при валидном промокоде. Промокод с `category_id` применяется только к товарам этой категории — остальные товары в заказе идут по полной цене.

---

### `GET /api/v1/orders/{id}/`

Возвращает заказ по ID со всеми позициями.

**Пример запроса:**
```
GET /api/v1/orders/1/
```

---

### `DELETE /api/v1/orders/{id}/`

Удаляет заказ по ID.

---

## Коды ошибок

| HTTP-код | Значение |
|---------|---------|
| `200 OK` | Успешный запрос |
| `201 Created` | Ресурс успешно создан |
| `204 No Content` | Ресурс успешно удалён |
| `400 Bad Request` | Ошибка валидации данных |
| `404 Not Found` | Ресурс не найден |

---

## Быстрый старт

Заполнить БД тестовыми данными:

```bash
python manage.py prepopulate_db
```

Очистить и заполнить заново:

```bash
python manage.py prepopulate_db --clear
```

Тестовые данные включают 3 пользователей, 3 категории, 6 товаров, 5 промокодов и 3 заказа.
