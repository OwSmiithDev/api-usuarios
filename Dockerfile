FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# slowapi's Limiter always opens ./.env; real .env stays out of the image (.dockerignore), config comes via env vars
RUN touch .env

# Run as an unprivileged user (least privilege; container breakout is not root on host)
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
