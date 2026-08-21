# Cloud Run image. Python only, no build step, no node.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY web/ ./web/
COPY data/ ./data/
COPY results/ ./results/

# The forecast cache and the schedule files are written at runtime.
RUN mkdir -p data/cache data/schedules

ENV PORT=8080
EXPOSE 8080
WORKDIR /app/src
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT} --workers 1
