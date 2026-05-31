# Todo Product

`Todo Product` это `API-first` приложение для задач на `FastAPI + PostgreSQL + Vue 3`, в котором уже есть роли пользователей, аудит действий, защита от слишком частых запросов, пагинация и сортировка задач, а также отдельный контур мониторинга.

По умолчанию production-конфиг сейчас настроен в лёгком режиме для очень слабых VPS: основной deploy поднимает только приложение и базу, а тяжёлые сервисы вынесены в профили и включаются вручную.

Для слабых серверов deploy теперь не собирает `api` и `web` на месте: образы собираются в `CI` и публикуются в `GHCR`, а сервер только скачивает их и запускает.

## Что умеет проект

- регистрация, вход, refresh и выход через `JWT access + refresh`
- роли `admin`, `vip`, `standard`
- CRUD задач, мягкое удаление и восстановление из архива
- пагинация, поиск и сортировка задач и архива
- профиль пользователя, аватар и смена пароля
- журнал аудита действий и HTTP-запросов
- административная панель с аналитикой по ролям, задачам и событиям
- rate limiting для auth, чтения и изменений
- метрики `Prometheus`, логи в `Loki`, визуализация в `Grafana`
- `pgAdmin` для работы с PostgreSQL

## Стек

### Backend

- `FastAPI`
- `SQLAlchemy 2`
- `Alembic`
- `PostgreSQL`
- `python-jose`
- `passlib`
- `prometheus-fastapi-instrumentator`

### Frontend

- `Vue 3`
- `Vite`
- `Pinia`
- `Vue Router`
- `Axios`

### Monitoring and Infra

- `Docker Compose`
- `Prometheus`
- `Grafana`
- `Loki + Promtail`
- `cAdvisor`
- `node-exporter`
- `postgres-exporter`
- `pgAdmin`

## Архитектура

```text
backend/
  app/
    api/           # роуты и зависимости
    core/          # конфиг, база, security, rate limiting
    models/        # SQLAlchemy модели
    repositories/  # доступ к данным
    schemas/       # Pydantic схемы
    services/      # бизнес-логика
    utils/         # файловые утилиты
  alembic/         # миграции
  tests/           # backend тесты

frontend/
  src/
    components/    # UI-компоненты
    lib/           # API-клиент и токены
    router/        # SPA маршруты
    stores/        # auth store
    views/         # страницы, включая admin

monitoring/
  prometheus/      # scrape config
  loki/            # log storage config
  promtail/        # log collector config
  grafana/         # provisioning datasources

scripts/server/
  bootstrap.sh     # установка Docker и Compose на Ubuntu
  deploy.sh        # production deploy с профилем monitoring
```

## Быстрый старт

### 1. Подготовьте `.env`

```bash
cp .env.example .env
```

Минимально заполните:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `PGADMIN_DEFAULT_PASSWORD`
- `GF_SECURITY_ADMIN_PASSWORD`
- `ADMIN_EMAILS`

Если хотите, чтобы первый пользователь сразу становился администратором, укажите его email в `ADMIN_EMAILS`.

### 2. Запуск приложения

Базовый стек:

```bash
docker compose up -d --build
```

Приложение вместе с мониторингом:

```bash
docker compose --profile monitoring up -d --build
```

`pgAdmin` при необходимости:

```bash
docker compose --profile admin-tools up -d pgadmin
```

После запуска доступны:

- приложение: `http://localhost:8081`
- backend docs: `http://localhost:8081/api/docs`
- pgAdmin: `http://localhost:5050`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`
- Loki: `http://localhost:3100`

## Роли пользователей

- `standard`:
  базовая работа с собственными задачами и профилем
- `vip`:
  тот же пользовательский поток, но роль хранится отдельно и доступна для внутренних тарифов или правил
- `admin`:
  доступ к `/admin`, обзору, аудиту и смене ролей пользователей

Админка умеет:

- показывать распределение пользователей по ролям
- выводить сводку по задачам
- отображать частые действия и коды ответов
- показывать горячие маршруты
- листать аудит по страницам
- менять роли пользователям без прямой работы с базой

## Аудит и безопасность

Проект сохраняет:

- события авторизации
- изменения задач
- обновления профиля и пароля
- удаления аккаунтов
- факт rate limit
- HTTP-контекст запроса: путь, метод, IP, статус, длительность, request id

Ограничения частоты запросов настраиваются через:

- `AUTH_RATE_LIMIT`
- `WRITE_RATE_LIMIT`
- `READ_RATE_LIMIT`

## Мониторинг

В проекте уже подготовлены:

- `Prometheus` для метрик API, PostgreSQL, контейнеров и сервера
- `Grafana` с автоматически подключёнными datasource
- `Grafana` с автоматически загружаемым dashboard `Todo Product Overview`
- `Loki + Promtail` для сбора Docker-логов
- `cAdvisor` для контейнерных метрик
- `node-exporter` для метрик хоста
- `postgres-exporter` для PostgreSQL

Готовый dashboard уже показывает:

- RPS backend API
- p95 latency
- распределение HTTP-статусов
- состояние PostgreSQL
- CPU хоста
- память контейнеров
- Docker-логи через `Loki`

Важно:

- сервисы мониторинга находятся в профиле `monitoring`
- `pgAdmin` вынесен в профиль `admin-tools`
- `promtail`, `cAdvisor` и `node-exporter` рассчитаны в первую очередь на Ubuntu/Linux сервер
- если открываете `3000`, `3100`, `9090`, `5050` наружу, ограничьте доступ через firewall или reverse proxy
- для очень слабого VPS сначала запускайте только базовый стек без дополнительных профилей

## Основные API-эндпоинты

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/tasks`
- `POST /api/v1/tasks`
- `PATCH /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/toggle`
- `DELETE /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/restore`
- `PATCH /api/v1/users/{user_id}/role`
- `GET /api/v1/admin/overview`
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/audit-events`

Для списка задач доступны параметры:

- `page`
- `page_size`
- `search`
- `status`
- `sort_by`
- `sort_order`
- `only_deleted`

## Тесты и проверки

### Backend

```bash
./.venv_backend/bin/pytest
```

Покрываются:

- регистрация, логин, refresh, logout
- rate limiting на авторизацию
- CRUD задач
- пагинация и сортировка
- архив и восстановление
- admin access и смена ролей

### Frontend

```bash
cd frontend
npm ci
npm run test
npm run build
```

Покрываются smoke-сценарии для:

- входа
- регистрации
- токен-хелперов
- списка задач

## CI/CD

### CI

Workflow `.github/workflows/ci.yml` автоматически делает:

1. backend dependency install
2. backend tests
3. frontend `npm ci`
4. frontend tests
5. frontend production build
6. сборку Docker-образов `api` и `web`
7. публикацию образов в `GHCR` при push в `master`
8. `docker compose --profile monitoring --profile admin-tools config`

### Deploy

Workflow `.github/workflows/deploy.yml` стартует только после успешного `CI` для ветки `master`.

На сервере выполняется:

1. `git fetch origin master`
2. `git reset --hard origin/master`
3. `bash scripts/server/bootstrap.sh`
4. `bash scripts/server/deploy.sh`

Что делает bootstrap:

- устанавливает `Docker`, если его ещё нет
- ставит `docker compose plugin`, если его не хватает
- запускает Docker service

Что делает deploy:

- создаёт `.env`, если его ещё нет
- валидирует базовый compose-конфиг
- очищает dangling Docker cache и неиспользуемые слои образов
- подтягивает `postgres`, `api` и `web` с ретраями
- поднимает проект через `docker compose up -d --no-build --remove-orphans`
- оставляет `pgAdmin` и monitoring выключенными по умолчанию

Важно:

- `git` на сервере должен быть установлен заранее
- SSH workflow рассчитан на Ubuntu-сервер
- каталог `/root/todo-app` считается deploy-копией, локальные изменения в отслеживаемых git-файлах будут сбрасываться
- `.env` сохраняется, потому что не отслеживается `git`
- для приватного `GHCR` можно добавить секреты `GHCR_USERNAME` и `GHCR_TOKEN`, для публичного репозитория это не обязательно
- дополнительные сервисы включаются вручную отдельными командами:
  `docker compose --profile admin-tools up -d pgadmin`
  `docker compose --profile monitoring up -d prometheus grafana loki promtail postgres-exporter cadvisor node-exporter`

## Переменные окружения

Ключевые переменные:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `DATABASE_URL`
- `ACCESS_TOKEN_TTL_MINUTES`
- `REFRESH_TOKEN_TTL_DAYS`
- `ADMIN_EMAILS`
- `AUTH_RATE_LIMIT`
- `WRITE_RATE_LIMIT`
- `READ_RATE_LIMIT`
- `METRICS_ENABLED`
- `GRAFANA_URL`
- `PROMETHEUS_URL`
- `LOKI_URL`
- `PGADMIN_URL`
- `GF_SECURITY_ADMIN_USER`
- `GF_SECURITY_ADMIN_PASSWORD`

## Что можно добавить дальше

- отдельные тарифные ограничения для `vip`
- экспорт аудита в `CSV`
- уведомления в Telegram или email при подозрительных событиях
- дашборды Grafana под конкретные SLA и бизнес-метрики

Скриншоты интерфейса и дополнительные картинки можно добавить позже без изменения архитектуры.
