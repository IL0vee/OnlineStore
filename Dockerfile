FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей Python
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего кода приложения
COPY . .

# Создание директории для логов
RUN mkdir -p logs

# Экспорт порта
EXPOSE 5000

# Переменные окружения
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Команда запуска приложения
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
