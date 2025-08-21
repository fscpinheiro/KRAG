FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
COPY data/ ./data/
RUN mkdir -p /app/chroma_db
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.address", "0.0.0.0"]