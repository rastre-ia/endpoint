from typing import Any, Dict, Sequence, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("GOOGLE_MODEL")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no ambiente.")

chat_model = ChatGoogleGenerativeAI(
    model=model,  
    google_api_key=google_api_key
)

prompt_template = """
Você é um assistente inteligente que ajuda os usuários a preencherem um formulário de denúncia. 
Sempre que o usuário fornecer informações relevantes, você deve organizar essas informações e gerar um relatório com o seguinte formato:


    "title": "{title}",
    "description": "{description}",
    "type": "{type}",
    "assistanceNeeded": "{assistanceNeeded}"



Certifique-se de usar valores válidos para os campos. 
Valores válidos para "Tipo de Denúncia": "strange_activity", "traffic", "peace_disturbance", "physical_assault", "robbery" ou "other". 
Valores válidos para "Necessita de Assistência": "require_assistance" ou "dont_require_assist".

Responda de forma clara e objetiva. Não mostre o JSON diretamente ao usuário, apenas gere a resposta.
"""

template = PromptTemplate(input_variables=["title", "description", "type", "assistanceNeeded"], template=prompt_template)

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

      
        context = {
            "title": "Exemplo de Título",  
            "description": "Descrição do caso aqui",
            "type": "strange_activity",
            "assistanceNeeded": "require_assistance",
        }

        prompt = template.format(**context)
        
        
        response = chat_model.invoke([{"role": "system", "content": prompt}] + messages)
        
        return {
            "response": response,
            "message": "Successfully generated chat response",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating chat response: {str(e)}")
