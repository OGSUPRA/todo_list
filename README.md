# TODO LIST — pet project (backend)

Небольшое веб-приложение для управления личными задачами. Проект сделан как учебный, но оформлен так, чтобы показать базовую архитектуру backend-приложения: слои `routes -> services -> db`, отдельные шаблоны и статика, и работа с SQLite.

## Что умеет
- Регистрация и вход пользователя (сессии Flask).
- Создание задач с названием и описанием.
- Просмотр списка задач пользователя.
- Изменение статуса задачи: `todo` ↔ `done`.
- Массовое завершение всех задач.
- Мягкое удаление (soft delete) и восстановление задач.
- Профиль пользователя: отображение имени и загрузка аватарки.
- Настройки пользователя: Изменение аватарки, пароля, имени.

## Стек
- Python 3.x
- Flask + Jinja2
- SQLite
- HTML/CSS (шаблоны в `backend/templates`, стили в `backend/static/css`)

## Архитектура и структура
- `backend/app.py` — маршруты и сессии, инициализация БД, загрузка аватаров.
- `backend/services/` — бизнес-логика:
  - `tasks.py` — CRUD по задачам и статусы.
  - `auth.py` — проверка пользователя.
  - `registration.py` — регистрация и проверка уникальности логина.
  - `users.py` — работа с профилем пользователя (аватар).
- `backend/db/` — доступ к SQLite и схема:
  - `database.py` — подключение.
  - `models.py` — создание таблиц `users` и `tasks`.

## Схема БД (кратко)
**users**
- `id`, `username`, `password`, `avatar_path`, `status_user`, `created_at`, `deleted_at`

**tasks**
- `id`, `user_id`, `title`, `description`, `status`, `created_at`, `deleted_at`

## Запуск
1. Установить зависимости:
```bash
pip install -r requirements.txt
```

2. Запустить приложение:
```bash
py backend/app.py
```

После запуска создается файл базы данных `todo.db` в корне проекта.

## Скриншоты
- Главная страница
![main](https://github.com/user-attachments/assets/e97c81c5-2d77-429f-9233-b0695d76317c)
- Авторизация
![login_user](https://github.com/user-attachments/assets/2e8c7e1f-7361-46bc-83d2-22cf16fa895c)
- Регистрация
![reg_user](https://github.com/user-attachments/assets/ae8854e7-eec2-4d10-b420-11dc6d681a81)
- Список задач
![tasks_users](https://github.com/user-attachments/assets/ed2436b1-c1d1-4599-8a77-c438febf6408)
- Корзина (удаленные задачи)
![tasks_del](https://github.com/user-attachments/assets/7fc414fa-5359-4ceb-8542-985426ea0785)
- Настройки профиля
![user_settings](https://github.com/user-attachments/assets/70be4989-4978-4d2a-b636-35ed9ba6b882)

## Роуты (основные)
- `/` — стартовая страница
- `/login`, `/registration` — авторизация и регистрация
- `/tasks` — список задач
- `/add`, `/done/<id>`, `/notdone/<id>`, `/delete/<id>` — действия над задачами
- `/deleted`, `/deleted/restore/<id>` — корзина и восстановление
- `/settings`, `/user/avatar` — настройки и загрузка аватара

## Что можно улучшить дальше
- Хэширование паролей (bcrypt/argon2).
- Валидация данных и обработка ошибок.
- Тесты сервисов и маршрутов (pytest).

---

Проект делался как учебный, но показывает базовые навыки backend‑разработки: работу с БД, архитектуру слоев, авторизацию, сессии, загрузку файлов и HTML‑шаблоны.
