FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY FrontEnd/frontend.py .
EXPOSE 8501
CMD streamlit run frontend.py --server. port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true