# 1. Usa a imagem oficial do Python (versão slim para ser leve e rápida)
FROM python:3.10-slim

# 2. Instala dependências de sistema necessárias para compilar bibliotecas como scikit-learn/pandas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Define o diretório de trabalho dentro do container
WORKDIR /app

# 4. Copia apenas o arquivo de requisitos primeiro (melhora a velocidade de builds futuros)
COPY requirements.txt .

# 5. Instala as dependências do projeto e o framework do GCP
# O scikit-learn e o functions-framework DEVEM estar no seu requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir functions-framework

# 6. Copia todo o código do bot para o diretório atual no container
COPY . .

# 7. Define variáveis de ambiente para otimizar o log do Python no GCP
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 8. Comando para iniciar o serviço na porta automática do Cloud Run ($PORT)
# O target aponta para a função handle_telegram definida no seu main.py
CMD exec functions-framework --target=handle_telegram --port=$PORT