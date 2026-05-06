FROM python:3.11-slim

WORKDIR /app

COPY agents/judge/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY shared /app/shared
RUN touch /app/shared/__init__.py

COPY agents/judge/agent.py /app/agent.py
COPY agents/judge/adk_app.py /app/adk_app.py

ENV PORT=8002
ENV PYTHONPATH=/app

EXPOSE 8002
CMD ["uvicorn", "adk_app:app", "--host", "0.0.0.0", "--port", "8002"]
