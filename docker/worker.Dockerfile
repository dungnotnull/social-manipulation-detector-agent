FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY prompts/ ./prompts/
COPY data/ ./data/
COPY scripts/ ./scripts/

ENV HF_HOME=/app/data/models
ENV TRANSFORMERS_CACHE=/app/data/models

CMD ["celery", "-A", "src.worker", "worker", "--loglevel=info", "--concurrency=4"]
