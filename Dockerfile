FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système (psycopg2 a besoin de libpq-dev)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8010

# Commande par défaut (gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ECORIDE.wsgi:application"]



