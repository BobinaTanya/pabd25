# Использовать официальный образ Python для базового изображения
FROM python:3.9-slim

# Установить рабочий каталог в контейнере на /app
WORKDIR /app

COPY requirements.txt .

# Установить необходимые пакеты, указанные в файле requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

RUN mkdir -p /app/logs

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=service/app.py
ENV FLASK_ENV=production

# Сделать порт 8000 доступным снаружи контейнера
EXPOSE 5000

# Запустить Gunicorn при запуске контейнера
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "service.app:app"] 