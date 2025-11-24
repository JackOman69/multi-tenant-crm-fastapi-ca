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
- Docker и Docker Compose

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

## Установка

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
# PostgreSQL Configuration (for docker-compose)
POSTGRES_USER=crm_user
POSTGRES_PASSWORD=crm_password
POSTGRES_DB=crm

# Database Configuration (for application)
DATABASE_URL=postgresql+asyncpg://crm_user:crm_password@db:5432/crm

# JWT
JWT_SECRET=change-me-in-production-min-32-chars-required
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12

# API Configuration
API_V1_PREFIX=/api/v1

# Application
DEBUG=false
```

**⚠️ Важно для production:**
- Измените `JWT_SECRET` на случайную строку минимум 32 символа
- Измените `POSTGRES_PASSWORD` на надёжный пароль
- Установите `DEBUG=false`

### 4. Запустите контейнеры

```bash
docker-compose up -d --build --no-deps
```

### 5. Проверьте работу

- **API:** http://localhost:8000
- **Документация:** http://localhost:8000/api/v1/docs
- **Health check:** http://localhost:8000/health


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

Проект содержит **57 тестов**, покрывающих все ключевые сценарии:

- **15 unit тестов** - базовая функциональность (config, database, domain)
- **32 property-based теста** - проверка инвариантов с Hypothesis
- **10 интеграционных тестов** - полный flow через API

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
- **57 тестов** с полным покрытием функциональности
- Property-based тесты с Hypothesis (32 теста)
- Unit тесты для всех слоёв (15 тестов)
- Интеграционные тесты через API (10 тестов)
- Запуск в Docker для изоляции окружения
