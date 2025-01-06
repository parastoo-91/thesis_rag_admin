FROM python:3.11

ENV OLLAMA_HOST=-
ENV EMBEDDING_MODEL=-
ENV CHROMADB_HTTPS_ADDRESS=- 
ENV CHROMADB_PORT=- 
ENV CHROMADB_COLLECTION=- 

WORKDIR /thesis_rag_admin



ADD main.py .



RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN  pip install -r requirements.txt

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

CMD ["streamlit","run", "main.py","--server.port=8502","--server.address=0.0.0.0"]
