FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# These defaults match docker-compose service configuration
ENV REDIS_HOST=redis \
    REDIS_PORT=6379 \
    REDIS_DB=0

COPY bot ./bot

CMD ["python", "-m", "bot.bot"]
