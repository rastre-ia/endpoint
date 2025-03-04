import os
import dotenv
from fastapi import  HTTPException, APIRouter
from pydantic import BaseModel
from langchain_google_genai import GoogleGenerativeAIEmbeddings

dotenv.load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise Exception("GOOGLE_API_KEY não definida no arquivo .env")

embedding = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)
router = APIRouter()


class TextInput(BaseModel):
    text: str

@router.post("/") 
async def generate_text_embeddings(data: TextInput):
    """
    Recebe um texto e gera os embeddings utilizando o Google Generative AI Embeddings.
    """
    try:
        embeddings = embedding.embed_query(data.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar os embeddings: {str(e)}")

    return {
        "embeddings": embeddings,
        "dimension": len(embeddings),
        "message": "Embeddings gerados com sucesso!"
    }
