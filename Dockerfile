FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini /alembic.ini
COPY alembic /alembic
COPY . /app

RUN chmod +x entrypoint.sh

EXPOSE 8000

# Démarrage
ENTRYPOINT ["./entrypoint.sh"]