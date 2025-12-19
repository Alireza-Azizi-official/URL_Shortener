FROM python:3.12-slim

WORKDIR /code



COPY requirements.txt /code/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /code

EXPOSE 8000


CMD ["uvicorn", "url_shortener.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
