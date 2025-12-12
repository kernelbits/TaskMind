FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY BackEnd/backend. py .

# Create data directory
RUN mkdir -p /app/data

EXPOSE 8000

# Railway requires CMD with shell form for $PORT expansion
CMD uvicorn backend:app --host 0.0.0.0 --port ${PORT:-8000}