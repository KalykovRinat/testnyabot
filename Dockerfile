FROM python:3.11-slim

# Обновление и установка системных зависимостей
RUN apt-get update && apt-get install -y build-essential

# Установка рабочей директории
WORKDIR /app

# Копируем все файлы в контейнер
COPY . .

# Создание виртуального окружения и установка зависимостей
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# Установка PATH к виртуальному окружению
ENV PATH="/opt/venv/bin:$PATH"

# Запуск бота
CMD ["python", "bot.py"]
