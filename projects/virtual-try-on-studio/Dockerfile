# Use slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Cloud Run requires the container to listen on $PORT (default 8080)
EXPOSE 8080

# Start the FastAPI app via main.py (which already runs uvicorn)
CMD ["python", "main.py"]
