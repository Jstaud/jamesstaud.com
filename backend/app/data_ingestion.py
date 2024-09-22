from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import os

# MongoDB connection setup
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
documents_collection = db["documents"]

# Embedding model initialization
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_data(text, source="manual"):
    """Ingest text data into MongoDB and generate embeddings."""
    # Generate embedding for the text
    embedding = embedding_model.encode(text).tolist()
    # Create document structure
    doc = {
        "text": text,
        "embedding": embedding,
        "metadata": {"source": source}
    }
    # Insert document into MongoDB
    documents_collection.insert_one(doc)
    print(f"Document from {source} ingested into MongoDB.")
