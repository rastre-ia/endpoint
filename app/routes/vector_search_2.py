from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
import os
from dotenv import load_dotenv
from langchain_community.embeddings import OllamaEmbeddings

# Carregar variáveis de ambiente
load_dotenv()

model_name = os.getenv("MODEL_NAME")
uri = os.getenv("MONGODB_URI")

ollama_emb = OllamaEmbeddings(model=model_name)

client = MongoClient(uri)
database = client["rastreia"]
index_name = "vector_index"
vector_field_name = "embeddings"

router = APIRouter()

# Modelo para a requisição do endpoint
class VectorSearchRequest(BaseModel):
    query: str  # O texto da consulta do usuário
    collection_name: str
    numCandidates: Optional[int] = 3  # Número de documentos mais relevantes a retornar
    limit: Optional[int] = 3          # Limite máximo de documentos no resultado

@router.post("/")
async def vector_search(request: VectorSearchRequest):
    """
    Realiza uma busca vetorial em uma coleção específica do banco de dados MongoDB usando embeddings.
    """
    try:
        query = request.query
        collection_name = request.collection_name
        numCandidates = request.numCandidates
        limit = request.limit

        # Verificar se a coleção existe no banco de dados
        if collection_name not in database.list_collection_names():
            raise HTTPException(
                status_code=400,
                detail=f"A coleção '{collection_name}' não existe no banco de dados.",
            )

        # Conectar-se à coleção MongoDB
        collection = database[collection_name]

        query_embedding = ollama_emb.embed_query(query)

        # Validar se o embedding foi gerado corretamente
        if not query_embedding or not isinstance(query_embedding, list):
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar o embedding para a consulta.",
            )

        # Adicionar logs para verificação
        print(f"query_embedding: {query_embedding}")

        pipeline = [
            {
                "$vectorSearch": {
                    "index": index_name,
                    "path": vector_field_name,
                    "queryVector": query_embedding,
                    "numCandidates": numCandidates,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "object": 1,
                    "objectDescription": 1,
                    "eventDescription": 1,
                    "eventDate": 1,
                    "suspectCharacteristics": 1,
                    "lat": {"$arrayElemAt": ["$location.coordinates", 1]},  
                    "long": {"$arrayElemAt": ["$location.coordinates", 0]},  
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        results = list(collection.aggregate(pipeline))

        return {
            "results": results,
            "message": "Busca vetorial concluída com sucesso.",
            "num_results": len(results),
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        # Adicionar log para verificar a exceção
        print(f"Exception: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao realizar a busca vetorial: {str(e)}"
        )
