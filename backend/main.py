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
    keywords = [
        "CV", "Resume", "job", "work", "experience", "skills", "abilities",
        "characteristics", "job application", "employment", "career", "professional",
        "work history", "qualifications", "achievements", "education", "training",
        "certifications", "work experience", "job history", "job skills", 
        "career summary", "career highlights", "career objectives", "employment history",
        "work profile", "professional background", "references", "recommendations", 
        "personal statement", "career accomplishments", "career progression", 
        "job duties", "responsibilities", "strengths", "key strengths", 
        "industry experience", "professional experience", "job qualifications",
        "professional summary", "background", "work history", 
        "skills and abilities", "accomplishments", "qualifications", 
        "achievements and awards", "education background", "academic qualifications",
        "work achievements", "work-related skills", "projects", "internships", 
        "volunteer work", "career development", "workplace skills", "job responsibilities", 
        "employment details", "professional journey", "summary of qualifications",
        "key achievements", "areas of expertise", "technical skills", "soft skills",
        "languages", "certificates", "professional certifications", "job applications",
        "employment objectives", "workplace achievements", "previous roles",
        "past positions", "workplace responsibilities", "leadership experience",
        "management skills", "communication skills", "teamwork", "problem-solving skills",
        "analytical skills", "professional memberships", "current position",
        "work goals", "career goals", "job performance", "employment record",
        "James Staud", "James", "Staud", "software developer", "AI", "backend development"
    ]
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that helps classify prompts as appropriate or inappropriate for a CV and Resume assistant. "
                "You are expected to be lenient and flexible, and consider most prompts appropriate unless they are clearly irrelevant "
                "or inappropriate for a professional context. Prompts that mention or imply work, experience, skills, professional development, "
                "career, or anything that could be loosely connected to professional or career-related topics should be considered appropriate. "
                "Even if the prompt is somewhat vague, it should still be classified as appropriate unless it is unmistakably unrelated "
                "to professional, career, or job-related contexts. Assume a broad interpretation of professional intent. "
                "If the prompt is appropriate, respond with only the word 'appropriate'. If it is clearly unrelated or inappropriate, "
                "respond with 'inappropriate'."
            )
        },
        {
            "role": "user",
            "content": f"Prompt: {prompt}"
        }
    ]
    
    # Add keywords contextually to the system prompt to encourage lenient matching
    messages[0]["content"] += "These are some examples of appropriate keywords and phrases: " + ", ".join(keywords) + "."

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=10,
        temperature=0.5
    )

    print(f"Classification response: {response.choices[0].message.content}")
    classification = response.choices[0].message.content.strip().lower()
    return classification == "appropriate"

@app.get("/")
def read_root():
    return {"message": "Welcome to my CV Assistant!"}

@app.post("/")
async def query(request: QueryRequest, api_key: str = Depends(get_api_key)):
    try:

        # Classify the prompt
        if not classify_prompt(request.question):
            raise HTTPException(status_code=400, detail="Inappropriate prompt")

        # Query LlamaIndex to retrieve relevant context
        context = query_llama_index(index, request.question)
        print(f"Retrieved context: {context}")
        # Generate response using OpenAI with retrieved context
        response = generate_response(request.question, context)
        return {"question": request.question, "answer": response}
    except Exception as e:
        print(f"An error occurred: {e}")
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
