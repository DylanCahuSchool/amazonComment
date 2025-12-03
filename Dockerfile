# Utiliser l'image Python 3.10 officielle
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt
COPY requirements.txt requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'application
COPY . .

# Exposer le port 8000 pour FastAPI
EXPOSE 8000

# Commande pour démarrer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]