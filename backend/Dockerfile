FROM python:3.12-slim

# Устанавливаем необходимые пакеты (curl + postgresql-client)
RUN apt-get update && apt-get install -y curl postgresql-client

# Создаем и переходим в рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Указываем команду по умолчанию (переопределится в docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]