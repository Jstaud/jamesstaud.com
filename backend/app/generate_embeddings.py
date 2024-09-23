import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from data_ingestion import ingest_data
from PyPDF2 import PdfReader  # You can also use pdfplumber for better text extraction
from dotenv import load_dotenv
from llama_indexing import setup_llama_index, query_llama_index  # Import LlamaIndex functions

# Load environment variables
load_dotenv()

# Initialize MongoDB and embedding model
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]  # Replace with your MongoDB database name
collection = db["embeddings"]  # Collection to store document embeddings

# Directory containing PDF documents
data_directory = "./data"

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
    
    # Set up LlamaIndex after processing PDFs
    index = setup_llama_index()
    print("LlamaIndex setup complete.")
    
    print("Finished processing PDFs.")