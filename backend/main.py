from fastapi import FastAPI, HTTPException
from llama_indexing import setup_llama_index, query_llama_index
import os
from dotenv import load_dotenv
from openai import OpenAI
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

@app.get("/")
def read_root():
    return {"message": "Welcome to my CV Assistant!"}

@app.post("/query")
async def query(request: QueryRequest):
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
