import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader  # You can also use pdfplumber for better text extraction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MongoDB and embedding model
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["mydatabase"]  # Replace with your MongoDB database name
collection = db["embeddings"]  # Collection to store document embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")  # Change model as per your needs

# Directory containing PDF documents
data_directory = "./data"

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    :param file_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""  # Extract text from each page
        return text.strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def generate_and_store_embedding(file_path):
    """
    Generates embeddings from extracted text of a PDF and stores them in MongoDB.
    :param file_path: Path to the PDF file.
    """
    text = extract_text_from_pdf(file_path)
    if not text:
        print(f"No text found in {file_path}. Skipping.")
        return

    # Generate embedding
    embedding = model.encode(text).tolist()

    # Document to insert into MongoDB
    doc = {
        "text": text,
        "embedding": embedding,
        "metadata": {
            "filename": os.path.basename(file_path),
            "filepath": file_path
        }
    }

    # Store in MongoDB
    collection.insert_one(doc)
    print(f"Embedding for {file_path} stored in MongoDB.")

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
    # Run the script to process PDFs and generate embeddings
    process_pdfs_in_directory(data_directory)
    print("Finished processing PDFs.")
