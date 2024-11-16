from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import OllamaEmbeddings
import ollama
import os

model_name = os.getenv("MODEL_NAME")

print(f"Model name: {model_name}")

ollama.pull(model_name)

# Inicializa o modelo OllamaEmbeddings
ollama_emb = OllamaEmbeddings(model=model_name)

# Cria o roteador para os endpoints
router = APIRouter()


# Define o esquema do payload de entrada
class TextInput(BaseModel):
    text: str


@router.post("/")
async def generate_text_embeddings(data: TextInput):
    """
    Recebe um texto e retorna os embeddings gerados.
    """
    try:
        # Gera os embeddings do texto fornecido
        embeddings = ollama_emb.embed_query(data.text)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao gerar embeddings: {str(e)}"
        )

    # Retorna os embeddings e a dimensão
    return {
        "embeddings": embeddings,
        "dimension": len(embeddings),
        "message": "Embeddings gerados com sucesso",
    }
