FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Usamos --threads para permitir que o Flask[async] processe as requisições sem travar
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app