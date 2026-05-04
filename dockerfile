FROM python:3.9-slim

WORKDIR /app

# Install Flask
RUN pip install flask --no-cache-dir

# Copy application files
COPY app.py .
COPY templates/ ./templates/

# Initialise the database on startup
ENV FLASK_APP=app.py

EXPOSE 5000

# Init DB then start the app
CMD ["sh", "-c", "python -c 'from app import init_db; init_db()' && python app.py"]
