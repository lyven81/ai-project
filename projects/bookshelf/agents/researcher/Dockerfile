FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY agents/researcher/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy shared/ first (relative imports)
COPY shared /app/shared
RUN touch /app/shared/__init__.py

# Copy agent code
COPY agents/researcher/agent.py /app/agent.py
COPY agents/researcher/adk_app.py /app/adk_app.py
COPY agents/researcher/data_tool.py /app/data_tool.py

# Copy bundled dataset (needed by Researcher's data_tool)
COPY dataset /app/dataset

ENV PORT=8001
ENV BOOKSHELF_DATASET_PATH=/app/dataset/dataset.xlsx
ENV PYTHONPATH=/app

EXPOSE 8001
CMD ["uvicorn", "adk_app:app", "--host", "0.0.0.0", "--port", "8001"]
