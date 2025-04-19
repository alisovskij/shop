FROM python:3.12-slim

RUN apt-get update && apt-get install -y curl postgresql-client

WORKDIR /backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "base.wsgi:application", "--bind", "0.0.0.0:8000"]