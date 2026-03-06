# Use a slim Python 3.11 base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies for PyMuPDF and Presidio
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the Spacy model required for Presidio Analyzer
RUN python -m spacy download en_core_web_lg

# Copy the rest of the application code
COPY . .

# Create a non-root user for security (Best practice for AWS Fargate)
RUN adduser --disabled-password --gecos '' cliniuser
RUN chown -R cliniuser:cliniuser /app
USER cliniuser

# Expose the FastAPI port
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "API:clini_clarity", "--host", "0.0.0.0", "--port", "8000"]