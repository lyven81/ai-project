# ---- Base image ----
FROM python:3.11-slim

# ---- System deps (curl for healthcheck, CA certs for TLS) ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential ca-certificates \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# ---- Workdir ----
WORKDIR /app

# ---- Python deps (cache-friendly) ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Create non-root user ----
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/bash appuser

# ---- App code ----
COPY . .

# ---- Change ownership ----
RUN chown -R appuser:appuser /app

# ---- Runtime env ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# ---- Healthcheck ----
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -fsS "http://localhost:${PORT}/healthz" || exit 1

# ---- Switch to non-root user ----
USER appuser

# ---- Expose & Start ----
EXPOSE 8080
CMD ["python", "app.py"]

# ---- Locale ----
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONIOENCODING=UTF-8
