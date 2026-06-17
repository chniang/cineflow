FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY app_complete.py .
COPY cineflow.db .
COPY style.css .
COPY .streamlit ./.streamlit

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 7860

# Lancer l'application
CMD ["streamlit", "run", "app_complete.py", "--server.port=7860", "--server.address=0.0.0.0"]
