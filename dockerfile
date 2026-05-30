FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем backend и остальные файлы
COPY backend/ ./backend/
COPY instance/ ./instance/
COPY static/ ./static/
# COPY todo.db ./

# Устанавливаем PYTHONPATH для импорта модулей из backend
ENV PYTHONPATH=/app/backend

# Создаём директории
RUN mkdir -p /app/instance /app/static/images

# Переходим в директорию backend для запуска
WORKDIR /app/backend

# Открываем порт
EXPOSE 5000

# Запускаем приложение (теперь app.py в папке backend)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
