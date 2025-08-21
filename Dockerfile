<<<<<<< HEAD
=======
# Image officielle Python
>>>>>>> e22fd4310173f3d31e026583f25eb34cf7355497
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

<<<<<<< HEAD

COPY . /app

RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
=======
COPY alembic.ini /alembic.ini
COPY alembic /alembic
COPY . /app

RUN chmod +x entrypoint.sh

EXPOSE 8000

# Démarrage
ENTRYPOINT ["./entrypoint.sh"]
>>>>>>> e22fd4310173f3d31e026583f25eb34cf7355497
