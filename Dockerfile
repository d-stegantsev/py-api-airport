FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "airport_service.wsgi:application", "--bind", "0.0.0.0:8000"]
