FROM python:3.12-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /code/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /code

EXPOSE 8000

# Use production-ready command
# For development with auto-reload, override CMD in docker-compose.yml:
# command: uvicorn url_shortener.app.main:app --host 0.0.0.0 --port 8000 --reload
CMD ["uvicorn", "url_shortener.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
