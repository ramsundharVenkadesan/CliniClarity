# Use a lightweight, official Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements first (this leverages Docker caching to speed up builds)
COPY requirements.txt .

# Install dependencies (no need for a virtual environment inside a container)
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_lg

# Copy the rest of your CliniClarity code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "RAG:rag_router", "--host", "0.0.0.0", "--port", "8000"]