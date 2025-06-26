FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

# Устанавливаем системные зависимости и затем Python-библиотеки
RUN apt-get update && \
    apt-get install -y gcc libffi-dev libssl-dev && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
