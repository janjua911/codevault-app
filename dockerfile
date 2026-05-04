FROM python:3.9-slim

WORKDIR /app

# Install Flask
RUN pip install flask

# Copy application files
COPY app.py .
COPY templates/ ./templates/

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
