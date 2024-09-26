import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI
from llama_indexing import setup_llama_index

# Load environment variables
load_dotenv()

# Initialize MongoDB and embedding model
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["jamesstaud"]  # Replace with your MongoDB database name
collection = db["cv_data"]  # Collection to store documents
embedding_collection = db["embeddings"]  # Collection to store embeddings

# OpenAI API key initialization
openAIClient = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID")
)

# Directory containing JSON documents
data_directory = "./data"

def get_embedding(text):
    """Generate embedding for the text using OpenAI API."""
    response = openAIClient.embeddings.create(
        input=text,
        model="text-embedding-ada-002",
        encoding_format="float"
    )
    return response.data[0].embedding

def ingest_data(data, source):
    """Ingest JSON data into MongoDB and generate embeddings."""
    # Convert JSON data to a textual format for embedding
    text = json.dumps(data, indent=2)
    embedding = get_embedding(text)  # Generate embedding for the text

    # Create document structure
    doc = {
        "data": data,
        "text": text,  # Add 'text' field for indexing purposes
        "embedding": embedding,
        "metadata": {"source": source}
    }

    # Replace old document or insert new one
    result = collection.replace_one(
        {"metadata.source": source},  # Filter to find the document by source
        doc,
        upsert=True  # Insert the document if it doesn't exist
    )
    if result.upserted_id:
        print(f"Document from {source} inserted into MongoDB with _id: {result.upserted_id}")
    else:
        print(f"Document from {source} replaced in MongoDB.")

def load_json_data(file_path):
    """
    Loads and returns JSON data from a file.
    :param file_path: Path to the JSON file.
    :return: Loaded JSON data as a dictionary.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        print(f"Error reading {file_path}: {e}")
        return None

def generate_and_store_embedding(file_path):
    """
    Generates embeddings from JSON data and stores them in MongoDB.
    :param file_path: Path to the JSON file.
    """
    data = load_json_data(file_path)
    if not data:
        print(f"No data found in {file_path}. Skipping.")
        return

    # Generate embedding and store to MongoDB
    ingest_data(data, source=file_path)

def remove_outdated_documents(directory):
    """
    Remove documents from MongoDB that do not have corresponding files in the data directory.
    :param directory: Directory containing JSON files.
    """
    # Get list of JSON files currently in the directory
    current_files = {os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith(".json")}

    # Get all documents currently stored in MongoDB
    stored_documents = collection.find({}, {"metadata.source": 1})
    stored_sources = {doc["metadata"]["source"] for doc in stored_documents}

    # Find outdated documents that are not in the current directory
    outdated_sources = stored_sources - current_files

    # Remove outdated documents
    for source in outdated_sources:
        collection.delete_one({"metadata.source": source})
        print(f"Removed outdated document: {source}")

def process_json_files_in_directory(directory):
    """
    Processes all JSON files in a given directory.
    :param directory: Directory containing JSON files.
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith(".json"):
            file_path = os.path.join(directory, filename)
            generate_and_store_embedding(file_path)

if __name__ == "__main__":
    print("running")
    # Run the script to process JSON files and generate embeddings
    process_json_files_in_directory(data_directory)

    # Remove documents not found in the current data directory
    remove_outdated_documents(data_directory)

    # Set up LlamaIndex after processing JSON files
    index = setup_llama_index(collection)
    print("LlamaIndex setup complete.")

    print("Finished processing JSON files.")
