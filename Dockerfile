FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Roda o nosso servidor Flask + Bot
CMD ["python", "main.py"]