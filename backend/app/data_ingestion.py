from openai import OpenAI
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB connection setup
mongo_uri = os.getenv("MONGODB_URI")
mongoClient = MongoClient(mongo_uri)
db = mongoClient["mydatabase"]
documents_collection = db["documents"]

# OpenAI API key initialization
openAIClient = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID"))

def get_embedding(text):
    """Generate embedding for the text using OpenAI API."""
    response = openAIClient.embeddings.create(
        input=text,
        model="text-embedding-ada-002", 
        encoding_format="float"
    )
    return response.data[0].embedding

def ingest_data(text, source="manual"):
    """Ingest text data into MongoDB and generate embeddings."""
    # Generate embedding for the text
    embedding = get_embedding(text)
    # Create document structure
    doc = {
        "text": text,
        "embedding": embedding,
        "metadata": {"source": source}
    }
    # Insert document into MongoDB
    documents_collection.insert_one(doc)
    print(f"Document from {source} ingested into MongoDB.")