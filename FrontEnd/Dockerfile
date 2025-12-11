# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend code
COPY FrontEnd/frontend.py .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the frontend
CMD ["streamlit", "run", "frontend.py", "--server.address", "0.0.0.0", "--server.port", "8501"]