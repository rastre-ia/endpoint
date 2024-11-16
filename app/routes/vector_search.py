from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from typing import List, Optional
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Conexão com o MongoDB
uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
database = client["rastreia"]

# Inicializa o roteador para os endpoints
router = APIRouter()

# Define o esquema do payload de entrada
class VectorSearchRequest(BaseModel):
    queryVector: List[float]
    collection_name: str
    numCandidates: Optional[int] = 3  # Padrão: 3
    limit: Optional[int] = 3  # Padrão: 3

@router.post("/")
async def vector_search(request: VectorSearchRequest):
    """
    Realiza uma busca vetorial na coleção especificada usando embeddings.
    """
    try:
        # Recuperar os dados da requisição
        query_vector = request.queryVector
        collection_name = request.collection_name
        num_candidates = request.numCandidates
        limit = request.limit

        # Verifica se a coleção existe
        if collection_name not in database.list_collection_names():
            raise HTTPException(
                status_code=400,
                detail=f"A coleção '{collection_name}' não existe no banco de dados.",
            )

        # Acessa a coleção
        collection = database[collection_name]

        # Define o pipeline de agregação
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embeddings",
                    "queryVector": query_vector,
                    "numCandidates": num_candidates,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "object": 1,
                    "objectDescription": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        # Executa a agregação
        results = list(collection.aggregate(pipeline))

        # Retorna os resultados
        return {
            "results": results,
            "message": "Busca vetorial realizada com sucesso",
            "num_results": len(results),
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao realizar a busca vetorial: {str(e)}"
        )
