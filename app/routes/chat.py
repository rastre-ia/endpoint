from typing import Any, Dict, Sequence, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o modelo de embeddings
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no ambiente.")

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  # Modelo de embeddings da Google
    google_api_key=google_api_key
)

router = APIRouter()

class ChatPayload(BaseModel):
    messages: Sequence[Dict[str, str]]
    options: Optional[Dict[str, Any]] = None

@router.post("/")
async def chat(payload: ChatPayload):
    """
    Receives a text and generates embeddings for it using Google Generative AI.
    """
    print("Processing chat request")
    print(payload)

    try:
        # Extrai o texto da última mensagem
        last_message = payload.messages[-1]
        text = last_message.get("content", "")

        if not text:
            raise HTTPException(status_code=400, detail="No text content found in the last message.")

        # Gera os embeddings
        embeddings = embeddings_model.embed_query(text)

        return {
            "embeddings": embeddings,
            "dimension": len(embeddings),
            "message": "Successfully generated embeddings",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating embeddings: {str(e)}")