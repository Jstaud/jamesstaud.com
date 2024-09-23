from fastapi import FastAPI, HTTPException
from app.llama_indexing import setup_llama_index, query_llama_index
from data_ingestion import ingest_data
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI()

# OpenAI API key initialization
openAIClient = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORGANIZATION_ID"))

# Initialize LlamaIndex and MongoDB
index = setup_llama_index()

@app.get("/")
def read_root():
    return {"message": "Welcome to my CV Assistant!"}

@app.post("/query")
async def query(question: str):
    try:
        # Query LlamaIndex to retrieve relevant context
        context = query_llama_index(index, question)
        # Generate response using OpenAI with retrieved context
        response = generate_response(question, context)
        return {"question": question, "answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_response(question: str, context: str):
    
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
    response = openAIClient.complete.create(
        engine="gpt-4o-mini",
        prompt=prompt,
        max_tokens=150,
        temperature=0.5
    )
    return response.choices[0].text.strip()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
