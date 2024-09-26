import os
from pymongo import MongoClient
from PyPDF2 import PdfReader  # You can also use pdfplumber for better text extraction
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
    organization=os.getenv("OPENAI_ORGANIZATION_ID"))


# Directory containing PDF documents
data_directory = "./data"

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


def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    :param file_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return text

def generate_and_store_embedding(file_path):
    """
    Generates embeddings from extracted text of a PDF and stores them in MongoDB.
    :param file_path: Path to the PDF file.
    """
    text = extract_text_from_pdf(file_path)
    if not text:
        print(f"No text found in {file_path}. Skipping.")
        return

    # Generate embedding and store to MongoDB
    ingest_data(text, source=file_path)

def remove_outdated_documents(directory):
    """
    Remove documents from MongoDB that do not have corresponding files in the data directory.
    :param directory: Directory containing PDF files.
    """
    # Get list of files currently in the directory
    current_files = {os.path.join(directory, filename) for filename in os.listdir(directory) if filename.lower().endswith(".pdf")}

    # Get all documents currently stored in MongoDB
    stored_documents = collection.find({}, {"metadata.source": 1})
    stored_sources = {doc["metadata"]["source"] for doc in stored_documents}

    # Find outdated documents that are not in the current directory
    outdated_sources = stored_sources - current_files

    # Remove outdated documents
    for source in outdated_sources:
        collection.delete_one({"metadata.source": source})
        print(f"Removed outdated document: {source}")

def process_pdfs_in_directory(directory):
    """
    Processes all PDF files in a given directory.
    :param directory: Directory containing PDF files.
    """
    for filename in os.listdir(directory):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            generate_and_store_embedding(file_path)

if __name__ == "__main__":
    print("running")
    # Run the script to process PDFs and generate embeddings
    process_pdfs_in_directory(data_directory)
    
    # Remove documents not found in the current data directory
    remove_outdated_documents(data_directory)
    
    # Set up LlamaIndex after processing PDFs
    index = setup_llama_index(collection)
    print("LlamaIndex setup complete.")
    
    print("Finished processing PDFs.")