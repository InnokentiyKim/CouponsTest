# Тестовое задание "Coupons and Orders"
Django-проект - система товаров и заказов с поддержкой купонов.

[![Coverage Status](https://img.shields.io/badge/coverage-90%25-success)](https://github.com/InnokentiyKim/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20?logo=django)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)

---

### Требования
- Python 3.10+
- Django 4.2+
- Docker (опционально)

### Установка и запуск

**Клонируйте репозиторий**
```bash
git clone <repository-url>
cd <project-directory>
```
### Вариант 1: Через Docker (рекомендуется)

```bash
# Собрать и запустить контейнеры
docker-compose up -d --build     

# Можно заполнить БД тестовыми данными, используя команду "prepopulate_db"
# Заполняет Users, Products, Categories, Coupons, Orders.
# --clear - удаляет все данные перед заполнением
docker exec -it myapp python manage.py prepopulate_db --clear 
````

### Вариант 2: Локально

```bash
# Создать виртуальное окружение и активировать
python -m venv venv
source venv/bin/activate  # macOS / Linux

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Заполнить БД тестовыми данными (опционально)
# --clear - удаляет все данные перед заполнением
python manage.py prepopulate_db --clear 

# Запустить сервер
python manage.py runserver
```


## Документация
Подробная документация доступна в файле [DOCUMENTATION.md](docs/DOCUMENTATION.md)

## Основные API endpoints

### Пользователь
```
GET    /api/v1/users/                     Список пользователей
POST   /api/v1/users/                     Создание пользователя
GET    /api/v1/users/<pk>/                Получение информации о пользователе
PUT    /api/v1/users/<pk>/                Обновление информации о пользователе
DELETE /api/v1/users/<pk>/                Удаление пользователя
```

### Категории
```
GET    /api/v1/categories/                Список категорий
POST   /api/v1/categories/                Создание категории
GET    /api/v1/categories/<pk>/           Получение информации о категории
PUT    /api/v1/categories/<pk>/           Обновление информации о категории
DELETE /api/v1/categories/<pk>/           Удаление категории
```

### Товары
```
GET    /api/v1/products/                  Список товаров
POST   /api/v1/products/                  Создание товара
GET    /api/v1/products/<pk>/             Получение информации о товаре
PUT    /api/v1/products/<pk>/             Обновление информации о товаре
DELETE /api/v1/products/<pk>/             Удаление товара
```

### Промокоды
```
GET    /api/v1/coupons/                   Список промокодов
POST   /api/v1/coupons/                   Создание промокода
GET    /api/v1/coupons/<pk>/              Получение информации о промокоде
PUT    /api/v1/coupons/<pk>/              Обновление информации о промокоде
DELETE /api/v1/coupons/<pk>/              Удаление промокода
```

### Заказы
```
GET    /api/v1/orders/                    Список заказов
POST   /api/v1/orders/                    Создание заказа
GET    /api/v1/orders/<pk>/               Получение информации о заказе
DELETE /api/v1/orders/<pk>/               Удаление заказа
```


## Тестирование

```bash
# Запуск всех тестов
pytest

# С отчетом о покрытии
pytest --cov=backend --cov-report=html

# Конкретный модуль
pytest tests/backend/test_api.py -v

# Запуск тестов внутри контейнера
docker exec -it myapp pytest
```





