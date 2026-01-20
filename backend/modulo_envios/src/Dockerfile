# Imagem base
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY ./src ./src

# Expõe porta da API
EXPOSE 8000

# Comando padrão: roda a API
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
