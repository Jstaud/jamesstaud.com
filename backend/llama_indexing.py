from pymongo import MongoClient
import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document

load_dotenv()

def query_llama_index(index, query):
    """Query LlamaIndex and return relevant context."""
    query_engine = index.as_query_engine()
    retrieved_docs = query_engine.query(query)
    return retrieved_docs
    # return " ".join([doc.text for doc in retrieved_docs])

def setup_llama_index(collection):
    """Sets up the LlamaIndex with existing documents from MongoDB."""
    docs = list(collection.find({}))
    llama_docs_dict = {}
    for doc in docs:
        # Convert MongoDB document into LlamaIndex Document format
        text = doc["text"]
        metadata = doc.get("metadata", {})
        source = metadata.get("source")
        
        # Use the source as a unique identifier to ensure replacement
        if source:
            llama_doc = Document(text=text, extra_info=metadata)
            llama_docs_dict[source] = llama_doc
    
    # Create the index from the list of LlamaIndex documents
    llama_docs = list(llama_docs_dict.values())
    index = VectorStoreIndex.from_documents(llama_docs)
    print("LlamaIndex setup complete.")
    return index