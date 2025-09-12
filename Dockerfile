# FROM python:3.10-slim

# # Installer dépendances système
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     python3-dev \
#     nginx \
#     supervisor \
#     && rm -rf /var/lib/apt/lists/*

# # Créer environnement virtuel
# RUN python3 -m venv /opt/venv
# ENV PATH="/opt/venv/bin:$PATH"

# # Répertoire de travail
# WORKDIR /app

# # Installer Python dependencies
# COPY requirements.txt .
# RUN pip install --upgrade pip && pip install -r requirements.txt && pip install supabase

# # Copier le code
# COPY . /app

# # Copier config Nginx et Supervisor
# COPY nginx.conf /etc/nginx/sites-available/default
# COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# # Exposer ports
# EXPOSE 80 443 8000

# # Lancer supervisord
# CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# Utiliser une image Python officielle

FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Créer un environnement virtuel et installer les dépendances
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Définir les variables d'environnement pour Python et l'environnement virtuel
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Lancer les migrations et démarrer Gunicorn
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000

