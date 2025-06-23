# Usa uma imagem base do Python
FROM python:3.11-bullseye

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl gnupg2 apt-transport-https ca-certificates \
    gcc g++ make unixodbc-dev libodbc1 odbcinst1debian2 libssl-dev \
 && curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
 && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia arquivos para o container
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Comando padrão
CMD ["python", "MapaAutomatico.py"]
