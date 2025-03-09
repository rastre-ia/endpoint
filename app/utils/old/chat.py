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

custom_prompt = PromptTemplate(
    input_variables=["messages"],
    template="""
Você é um assistente de inteligência artificial especializado em ajudar a polícia na criação de relatórios de objetos **roubados** ou **achados**. 
Seu objetivo é coletar todas as informações necessárias de forma clara e organizada.

Sempre guie o usuário fazendo perguntas para coletar detalhes essenciais, como:
- **Objeto**: Qual é o tipo do objeto? (celular, bicicleta, bolsa, carteira, etc.)
- **Marca/Modelo**: Se aplicável, qual é a marca e o modelo?
- **Descrição**: Qual a cor e alguma característica distintiva?
- **Data/Hora**: Quando o roubo/achado ocorreu?
- **Local**: Onde exatamente o evento aconteceu? (endereço ou ponto de referência)
- **Identificação**: O objeto tem número de série, IMEI ou alguma etiqueta de identificação?
- **Proprietário**: O usuário sabe quem é o dono ou tem alguma informação de contato?

Se o usuário fornecer informações incompletas, continue perguntando de forma educada até que o relato esteja completo.

Histórico da conversa:
{messages}
""",
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
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in payload.messages]

        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided.")

        formatted_prompt = custom_prompt.format(messages=messages)

        response = chat_model.invoke(formatted_prompt)


        return {
            "response": response,
            "message": "Successfully generated chat response",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating chat response: {str(e)}")
