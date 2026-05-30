# Todo Product

Полноценный `API-first` Todo-проект, собранный как современное веб-приложение:

- `FastAPI` вместо Flask
- `PostgreSQL` вместо SQLite
- `JWT access + refresh` вместо серверных сессий
- `Vue 3 + Vite` вместо серверных HTML-шаблонов
- `pgAdmin` вместо SQLite web admin

Проект разделён на backend API, frontend SPA и production-ready Docker-инфраструктуру.

## Что умеет

- регистрация и вход пользователя
- авторизация через JWT
- refresh-механизм для продления сессии
- CRUD по задачам
- переключение статуса `todo/done`
- массовое завершение задач
- мягкое удаление и восстановление из архива
- редактирование профиля
- смена пароля
- загрузка аватара
- SQL-админка для PostgreSQL через `pgAdmin`

## Стек

### Backend

- `FastAPI`
- `SQLAlchemy 2`
- `Alembic`
- `PostgreSQL`
- `python-jose`
- `passlib`

### Frontend

- `Vue 3`
- `Vite`
- `Pinia`
- `Vue Router`
- `Axios`

### Infrastructure

- `Docker Compose`
- `Nginx` внутри frontend-контейнера
- `pgAdmin 4`

## Архитектура

```text
backend/
  app/
    api/           # роуты и зависимости
    core/          # конфиг, база, security
    models/        # SQLAlchemy модели
    repositories/  # слой доступа к данным
    schemas/       # Pydantic схемы
    services/      # бизнес-логика
    utils/         # файловые утилиты
  alembic/         # миграции
  tests/           # backend тесты

frontend/
  src/
    components/    # UI-компоненты
    lib/           # API-клиент, токены
    router/        # маршруты
    stores/        # auth store
    views/         # страницы SPA
    tests/         # frontend setup
```

## Быстрый старт

### 1. Подготовка окружения

Создайте `.env` на основе примера:

```bash
cp .env.example .env
```

Минимум, что нужно изменить:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `PGADMIN_DEFAULT_PASSWORD`

### 2. Запуск через Docker

```bash
docker compose up -d --build
```

После запуска:

- приложение: `http://localhost:8081`
- backend docs: `http://localhost:8081/api/docs`
- pgAdmin: `http://localhost:5050`

## Переменные окружения

Основные переменные из `.env.example`:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `DATABASE_URL`
- `ACCESS_TOKEN_TTL_MINUTES`
- `REFRESH_TOKEN_TTL_DAYS`
- `CORS_ORIGINS`
- `MEDIA_ROOT`
- `SECURE_COOKIES`
- `PGADMIN_DEFAULT_EMAIL`
- `PGADMIN_DEFAULT_PASSWORD`

## Backend API

Основные группы эндпоинтов:

- `/api/v1/auth`
- `/api/v1/tasks`
- `/api/v1/users`
- `/api/v1/health`

Ключевые сценарии:

- `POST /api/v1/auth/register` — регистрация
- `POST /api/v1/auth/login` — вход
- `POST /api/v1/auth/refresh` — refresh access token
- `POST /api/v1/auth/logout` — выход
- `GET /api/v1/users/me` — получить профиль
- `PATCH /api/v1/users/me` — обновить профиль
- `POST /api/v1/users/me/password` — сменить пароль
- `POST /api/v1/users/me/avatar` — обновить аватар
- `GET /api/v1/tasks` — список задач
- `POST /api/v1/tasks` — создать задачу
- `PATCH /api/v1/tasks/{task_id}` — обновить задачу
- `POST /api/v1/tasks/{task_id}/toggle` — переключить статус
- `DELETE /api/v1/tasks/{task_id}` — отправить в архив
- `POST /api/v1/tasks/{task_id}/restore` — восстановить

## Тесты

### Backend

```bash
pytest
```

Покрываются основные сценарии:

- регистрация, логин, refresh, logout
- CRUD задач
- архив и восстановление
- профиль, аватар, пароль, удаление аккаунта

### Frontend

```bash
cd frontend
npm ci
npm run test
```

Есть smoke-тесты для:

- token helpers
- формы входа
- списка задач

## Деплой

В репозитории есть два workflow:

- `.github/workflows/ci.yml` — тесты и сборка
- `.github/workflows/deploy.yml` — деплой только после успешного CI

Сценарий:

1. push в `master` запускает CI
2. backend-тесты и frontend-проверки проходят автоматически
3. CI дополнительно собирает Docker-образы `api` и `web`
4. только если весь CI завершился успешно, запускается deploy workflow
5. GitHub Actions подключается по SSH к серверу
6. выполняет `git pull`
7. поднимает стек через `docker compose up -d --build --remove-orphans`

Перед первым деплоем нужно:

- подготовить `.env` на сервере
- убедиться, что Docker и Docker Compose установлены

## Что уже улучшено по сравнению со старой версией

- убран серверный HTML-рендеринг
- убрана привязка к SQLite
- добавлено разделение на слои `api / services / repositories / models`
- введены миграции Alembic
- авторизация переведена на JWT
- frontend вынесен в отдельное приложение
- добавлены тесты
- docker-инфраструктура упрощена и очищена

## Что можно добавить позже

- rate limiting
- аудит действий пользователя
- пагинацию и сортировки задач
- роли пользователей

Скриншоты и картинки можно добавить позже без изменения архитектуры.
