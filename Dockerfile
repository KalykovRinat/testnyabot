FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN python --version && pip --version && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
