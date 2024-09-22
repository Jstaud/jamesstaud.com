from llama_index import Document, GPTSimpleVectorIndex
from pymongo import MongoClient
import os

# MongoDB connection setup
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]
documents_collection = db["documents"]

# Initialize an empty LlamaIndex
index = GPTSimpleVectorIndex([])

def setup_llama_index():
    """Sets up the LlamaIndex with existing documents from MongoDB."""
    docs = list(documents_collection.find({}))
    for doc in docs:
        # Convert MongoDB document into LlamaIndex Document format
        text = doc["text"]
        metadata = doc.get("metadata", {})
        llama_doc = Document(text=text, extra_info=metadata)
        index.add(llama_doc)
    print("LlamaIndex setup complete.")
    return index

def query_llama_index(index, query):
    """Query LlamaIndex and return relevant context."""
    retrieved_docs = index.query(query)
    return " ".join([doc.text for doc in retrieved_docs])
