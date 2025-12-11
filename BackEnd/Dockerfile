# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements. txt

# Copy backend code
COPY BackEnd/backend.py .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the backend
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]