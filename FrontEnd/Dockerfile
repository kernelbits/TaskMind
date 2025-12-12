FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements. txt

# Copy frontend code
COPY FrontEnd/frontend.py .

EXPOSE 8501

# Railway requires CMD with shell form for $PORT expansion
CMD streamlit run frontend.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true