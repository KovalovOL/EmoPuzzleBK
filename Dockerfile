FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt tensorflow-cpu==2.11.0

COPY . .

ENV PYTHONPATH=/app \
    TF_CPP_MIN_LOG_LEVEL=3 \
    MODE=production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]