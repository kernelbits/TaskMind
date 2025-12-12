FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY BackEnd/backend. py .

# Create data directory
RUN mkdir -p /app/data

# Expose port (Render uses PORT env var)
EXPOSE 8000

# Use PORT from environment (Render requirement)
CMD uvicorn backend:app --host 0.0.0.0 --port ${PORT:-8000}