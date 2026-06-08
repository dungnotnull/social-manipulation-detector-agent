FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY prompts/ ./prompts/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY .env.example ./.env.example

ENV HF_HOME=/app/data/models
ENV TRANSFORMERS_CACHE=/app/data/models

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
