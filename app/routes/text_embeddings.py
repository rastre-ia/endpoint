from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import OllamaEmbeddings
import ollama
from dotenv import load_dotenv
import os


load_dotenv()
model_name = os.getenv("MODEL_NAME")

print(f"Model name: {model_name}")

ollama.pull(model_name)

ollama_emb = OllamaEmbeddings(model=model_name)

router = APIRouter()


class TextInput(BaseModel):
    text: str


@router.post("/")
async def generate_text_embeddings(data: TextInput):
    """
    Receives a text and generates embeddings for it.
    """
    try:
        embeddings = ollama_emb.embed_query(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating: {str(e)}")

    return {
        "embeddings": embeddings,
        "dimension": len(embeddings),
        "message": "Successfully generating embeddings",
    }
