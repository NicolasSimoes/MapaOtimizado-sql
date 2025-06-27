FROM python:3.11-bullseye

WORKDIR /app

# Instala dependências do sistema e ODBC do SQL Server
RUN apt-get update && apt-get install -y \
    curl gnupg2 apt-transport-https ca-certificates \
    gcc g++ make unixodbc-dev libodbc1 odbcinst1debian2 libssl-dev \
 && curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc \
 && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
 && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define que os prints e logs aparecem em tempo real
ENV PYTHONUNBUFFERED=1

# Instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todos os arquivos da aplicação
COPY . .

# Comando para rodar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app", "--timeout", "300"]
