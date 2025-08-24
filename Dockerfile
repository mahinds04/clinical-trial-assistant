FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_deployment.txt .
RUN pip3 install -r requirements_deployment.txt

# Copy application code
COPY . .

# Create data directory and copy demo data
RUN mkdir -p data
COPY data/clin_trials_demo.csv data/

# Set environment variables
ENV DEPLOYMENT_ENV=cloud
ENV PYTHONPATH=/app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]