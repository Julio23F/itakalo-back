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



# --- Étape 1 : image de base ---
FROM python:3.12-slim

# --- Étape 2 : installer les dépendances système nécessaires ---
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# --- Étape 3 : définir le répertoire de travail ---
WORKDIR /app

# --- Étape 4 : copier requirements.txt et installer les dépendances ---
COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r requirements.txt

# --- Étape 5 : copier tout le code de l'application ---
COPY . .

# --- Étape 6 : définir l'environnement Python et l'environnement virtuel ---
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# --- Étape 7 : exposer le port de l'application ---
EXPOSE 8000

# --- Étape 8 : exécuter les migrations puis démarrer Gunicorn ---
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3"]



