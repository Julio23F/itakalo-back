FROM python:3.10-slim

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Créer environnement virtuel
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Répertoire de travail
WORKDIR /app

# Copier requirements + installer dépendances
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install supabase

# Copier code
COPY . /app

# Config Nginx
COPY nginx.conf /etc/nginx/sites-available/default

# Config Supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exposer ports
EXPOSE 80

# Lancer supervisord (qui gère Daphne + Nginx)
CMD ["/usr/bin/supervisord", "-n"]
