from fastapi import FastAPI, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from llama_indexing import setup_llama_index, query_llama_index
import os
from dotenv import load_dotenv
from openai import OpenAI, completions
from pymongo import MongoClient
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

# MongoDB connection setup
mongo_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongo_uri)
db = client["jamesstaud"]
documents_collection = db["cv_data"]

# OpenAI API key initialization
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID"))

# Initialize LlamaIndex and MongoDB
index = setup_llama_index(documents_collection)

class QueryRequest(BaseModel):
    question: str

# API Key authentication
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

def classify_prompt(prompt: str) -> bool:
    """
    Classify the prompt to ensure it is appropriate for the intended use case.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        prompt=f"Classify the following prompt as appropriate or inappropriate for a CV and Resume assistant. If it's appropriate, respond with only the word 'appropriate', if it's inappropriate, respond with 'inappropriate': {prompt}",
        max_tokens=10
    )
    classification = response.choices[0].message
    return classification == "appropriate"

@app.get("/")
def read_root():
    return {"message": "Welcome to my CV Assistant!"}

@app.post("/")
async def query(request: QueryRequest, api_key: str = Depends(get_api_key)):
    try:
        # Query LlamaIndex to retrieve relevant context
        context = query_llama_index(index, request.question)
        print(f"Retrieved context: {context}")
        # Generate response using OpenAI with retrieved context
        response = generate_response(request.question, context)
        return {"question": request.question, "answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_response(question: str, context: str):
    messages = [
        {"role": "system", "content": "You are an assistant that helps users learn more about James Staud's CV and promotes his skills, experiences, abilities, and characteristics to the user. You've been given context from a RAG search. Provide detailed and informative answers based on the provided context. Focus on the provided context and answer the user's questions and give relevant examples of skills, experience, and supporting evidence where applicable."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}\nAnswer:"}
    ]
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=150,
        temperature=0.5
    )
    return response.choices[0].message

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
