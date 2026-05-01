# Use the official lightweight Python image
# 3.11 is highly stable for LangChain, FastAPI, and data science libraries
FROM python:3.11-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy just the requirements first to leverage Docker cache
# This way, Docker only reinstalls packages if requirements.txt changes
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


RUN python -c "from transformers import pipeline; pipeline('text-classification', model='protectai/deberta-v3-base-prompt-injection-v2')"

# Copy the rest of your application code
# This includes API.py, RAG.py, REACT.py, and your templates folder
COPY . .

# Expose port 8080 (The default port for Google Cloud Run)
EXPOSE 8080

# Command to run the application using Uvicorn
# Syntax: <filename_without_.py>:<fastapi_instance_name>
CMD ["uvicorn", "API:clini_clarity", "--host", "0.0.0.0", "--port", "8080"]