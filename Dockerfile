FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Porta padrão do Cloud Run
ENV PORT 8080
CMD ["python", "main.py"]