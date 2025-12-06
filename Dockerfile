FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

WORKDIR $APP_HOME


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY url_shortener ./url_shortener


ARG APP_PORT=8000
EXPOSE $APP_PORT


CMD ["uvicorn", "url_shortener.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
