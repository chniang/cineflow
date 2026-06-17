FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY app_complete.py .
COPY tidiane_flix.db .
COPY style.css .
COPY .streamlit ./.streamlit

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8501

# Lancer l'application
CMD ["streamlit", "run", "app_complete.py", "--server.port=8501", "--server.address=0.0.0.0"]
