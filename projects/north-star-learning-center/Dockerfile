FROM python:3.11-slim

WORKDIR /app

# Install Python deps first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY main.py demo.html data.db ./

# Cloud Run injects PORT; we honour it (default 8080)
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
