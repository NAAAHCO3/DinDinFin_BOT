# Usa a imagem oficial do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Adiciona o framework necessário para o GCP
RUN pip install functions-framework

# Copia o restante do código
COPY . .

# Comando para iniciar o serviço na porta definida pelo GCP
CMD exec functions-framework --target=handle_telegram --port=$PORT