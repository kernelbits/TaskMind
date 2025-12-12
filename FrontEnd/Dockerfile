FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt . 

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY FrontEnd/frontend.py .

# Expose port
EXPOSE 8501

# Run Streamlit (Render uses PORT env var)
CMD streamlit run frontend.py --server.port=${PORT:-8501} --server. address=0.0.0.0