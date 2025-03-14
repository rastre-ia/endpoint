from typing import Any, Dict, Sequence, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a chave da API
google_api_key = os.getenv("GOOGLE_API_KEY")
model =os.getenv("GOOGLE_MODEL")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no ambiente.")

# Inicializa o modelo de chat
chat_model = ChatGoogleGenerativeAI(
    model=model,  # Ou outro modelo adequado
    google_api_key=google_api_key
)

router = APIRouter()

class ChatPayload(BaseModel):
    messages: Sequence[Dict[str, str]]
    options: Optional[Dict[str, Any]] = None

@router.post("/")
async def chat(payload: ChatPayload):
    """
    Recebe mensagens do usuário e retorna uma resposta do modelo de chat.
    """
    print("Processing chat request")
    print(payload)

    try:
        # Prepara o histórico da conversa para o modelo
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in payload.messages]

        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided.")

        # Obtém a resposta do modelo de chat
        response = chat_model.invoke(messages)

        return {
            "response": response,
            "message": "Successfully generated chat response",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating chat response: {str(e)}")
