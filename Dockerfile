FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

ENV PYTHONPATH=/app/src

# Train model and generate artifacts inside the image
RUN python src/credit_risk/train.py

EXPOSE 8000

CMD ["sh", "-c", "uvicorn credit_risk.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]