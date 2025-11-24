# Multi-Tenant CRM

CRM система с поддержкой нескольких организаций на FastAPI и PostgreSQL.

## Архитектура

Проект следует принципам Clean Architecture с явным разделением слоёв:

- **Domain Layer** (`src/domain/`) - бизнес-логика, entities, исключения
- **Application Layer** (`src/services/`) - use cases, бизнес-сервисы
- **Infrastructure Layer** (`src/repositories/`, `src/db/`) - работа с БД, SQLAlchemy модели
- **Presentation Layer** (`src/api/`) - REST API endpoints, schemas, middleware

## Требования

- Python 3.11+
- PostgreSQL 15+
- uv (для управления зависимостями)
- Docker и Docker Compose (опционально)

## Технологический стек

### Backend
- **FastAPI** - современный async веб-фреймворк
- **SQLAlchemy 2.0** - ORM с async поддержкой
- **Alembic** - миграции базы данных
- **Pydantic** - валидация данных и настройки
- **asyncpg** - async драйвер PostgreSQL

### Безопасность
- **PyJWT** - JWT токены для аутентификации
- **bcrypt** - хеширование паролей

### Тестирование
- **pytest** - фреймворк для тестирования
- **pytest-asyncio** - поддержка async тестов
- **Hypothesis** - property-based тестирование
- **httpx** - HTTP клиент для тестирования API

### Качество кода
- **Ruff** - быстрый линтер и форматтер

## Быстрый старт с Docker

1. Скопируйте `.env.example` в `.env` и настройте переменные:

```bash
cp .env.example .env
```

**Важно:** Измените `JWT_SECRET` на случайную строку минимум 32 символа для production!

2. Запустите контейнеры:

```bash
docker-compose up -d
```

API будет доступен: http://localhost:8000

Документация API: http://localhost:8000/api/v1/docs

**Примечание:** Файл `.env` содержит чувствительные данные и не должен попадать в git (добавлен в `.gitignore`).

## Локальная установка

### 1. Установите uv

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Установите зависимости

```bash
uv sync
```

### 3. Настройте переменные окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Пример `.env`:
```
DATABASE_URL=postgresql+asyncpg://crm_user:crm_password@localhost:5432/crm
JWT_SECRET=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
API_V1_PREFIX=/api/v1
```

### 4. Запустите PostgreSQL

```bash
docker run -d \
  --name crm-postgres \
  -e POSTGRES_USER=crm_user \
  -e POSTGRES_PASSWORD=crm_password \
  -e POSTGRES_DB=crm \
  -p 5432:5432 \
  postgres:16-alpine
```

### 5. Примените миграции

```bash
uv run alembic upgrade head
```

### 6. Запустите приложение

```bash
uv run uvicorn src.main:app --reload
```

API: http://localhost:8000

Документация: http://localhost:8000/api/v1/docs

## Примеры API запросов

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe",
    "organization_name": "My Company"
  }'
```

### Логин

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Получение списка организаций

```bash
curl -X GET http://localhost:8000/api/v1/organizations/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Создание контакта

```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Organization-Id: YOUR_ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1234567890"
  }'
```

### Создание сделки

```bash
curl -X POST http://localhost:8000/api/v1/deals \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Organization-Id: YOUR_ORG_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "CONTACT_UUID",
    "title": "Big Deal",
    "amount": "10000.00",
    "currency": "USD"
  }'
```

### Получение аналитики

```bash
curl -X GET http://localhost:8000/api/v1/analytics/deals/summary \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "X-Organization-Id: YOUR_ORG_ID"
```

## Тестирование

Проект содержит **49 тестов**, покрывающих все ключевые сценарии:

- **13 unit тестов** - базовая функциональность (config, database, domain)
- **33 property-based теста** - проверка инвариантов с Hypothesis
- **3 интеграционных теста** - полный flow через API

### Запуск всех тестов через Docker

Рекомендуемый способ - запуск в изолированном окружении:

```bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

Или с пересборкой:

```bash
docker-compose -f docker-compose.test.yml down
docker-compose -f docker-compose.test.yml build test_runner
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Запуск тестов локально

```bash
# Все тесты
uv run pytest -v

# Только unit тесты
uv run pytest tests/test_*.py -v

# Только property-based тесты
uv run pytest tests/properties/ -v

# Только интеграционные тесты (требуется PostgreSQL)
uv run pytest tests/integration/ -v
```

### Запуск с покрытием

```bash
uv run pytest --cov=src --cov-report=html --cov-report=term
```

Отчёт будет в `htmlcov/index.html`

### Запуск конкретного теста

```bash
uv run pytest tests/properties/test_services.py::test_deal_initial_state -v
```

### Категории тестов

**Unit тесты** (`tests/test_*.py`):
- Конфигурация приложения
- Подключение к БД
- Domain entities и enums
- Базовая валидация

**Property-based тесты** (`tests/properties/`):
- `test_security.py` - хеширование паролей, JWT токены
- `test_api.py` - изоляция организаций, заголовки
- `test_permissions.py` - ролевая модель, права доступа
- `test_services.py` - бизнес-логика сервисов (33 теста)

**Интеграционные тесты** (`tests/integration/`):
- `test_analytics_integration.py` - полный flow аналитики через API

## Линтинг

```bash
uv run ruff check src/ tests/
```

Автоисправление:

```bash
uv run ruff check src/ tests/ --fix
```

## Миграции базы данных

### Создание новой миграции

```bash
uv run alembic revision --autogenerate -m "Description"
```

### Применение миграций

```bash
uv run alembic upgrade head
```

### Откат миграции

```bash
uv run alembic downgrade -1
```

## Структура проекта

```
.
├── src/
│   ├── api/
│   │   ├── middleware/       # Обработка ошибок
│   │   └── v1/
│   │       ├── endpoints/    # API роутеры
│   │       └── schemas/      # Pydantic схемы
│   ├── core/                 # Конфигурация, security
│   ├── db/                   # SQLAlchemy модели, сессии
│   ├── domain/               # Entities, исключения
│   ├── repositories/         # Репозитории для работы с БД
│   ├── services/             # Бизнес-логика
│   └── main.py              # Точка входа FastAPI
├── alembic/                  # Миграции БД
├── tests/
│   ├── properties/           # Property-based тесты
│   ├── unit/                 # Unit тесты
│   └── integration/          # Интеграционные тесты
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Основные возможности

### Multi-tenant архитектура
- Полная изоляция данных между организациями
- Заголовок `X-Organization-Id` для контекста организации

### Ролевая модель доступа
- **Owner** - полный доступ ко всем ресурсам
- **Admin** - управление ресурсами, откат стадий сделок
- **Manager** - создание и управление своими ресурсами
- **Member** - ограниченный доступ к своим ресурсам

### Управление сущностями
- **Контакты** - CRUD, поиск, пагинация
- **Сделки** - управление воронкой, статусы, стадии
- **Задачи** - привязка к сделкам, фильтрация
- **Активности** - таймлайн событий по сделкам

### Аналитика
- Сводка по сделкам (количество, суммы, средние)
- Воронка продаж по стадиям
- Кеширование результатов

### Безопасность
- JWT аутентификация (access + refresh токены)
- Bcrypt хеширование паролей
- Проверка прав доступа на уровне сервисов

### Тестирование
- **49 тестов** с полным покрытием функциональности
- Property-based тесты с Hypothesis (33 теста)
- Unit тесты для всех слоёв (13 тестов)
- Интеграционные тесты через API (3 теста)
- Запуск в Docker для изоляции окружения
