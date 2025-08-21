import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "devstral:24b")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    # ChromaDB
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

    # Processamento
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "5"))

    # Paths
    SOURCE_CODE_PATH = "./data/source_code"
    DOCS_PATH = "./data/docs"

    # Debug
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"