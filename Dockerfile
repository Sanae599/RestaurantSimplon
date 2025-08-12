# Image officielle Python
FROM python:3.12-slim

# Dossier de travail
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l’application
COPY . .

# Exposer le port de l’API
EXPOSE 8000

# Commande de démarrage (Uvicorn)
ENTRYPOINT ["/entrypoint.sh"]
