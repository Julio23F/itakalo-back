FROM python:3.10-slim

# Installer les bibliothèques système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer et activer l'environnement virtuel
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier le code et installer les dépendances
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install supabase

# Commande à exécuter au démarrage
#CMD ["/bin/bash", "-c", "python manage.py migrate && gunicorn config.wsgi"]
# CMD ["/bin/bash", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 config.asgi:application"]
CMD ["/bin/bash", "-c", "python manage.py migrate && daphne config.asgi:application"]
