from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo.mongo_client import MongoClient
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI")
client = MongoClient(uri)
database = client["rastreia"]


router = APIRouter()


class VectorSearchRequest(BaseModel):
    queryVector: List[float]
    collection_name: str
    numCandidates: Optional[int] = 3 
    limit: Optional[int] = 3  

@router.post("/")
async def vector_search(request: VectorSearchRequest):
    """
    Performs a vector search in the specified collection using embeddings
       
    """
    try:
        query_vector = request.queryVector
        collection_name = request.collection_name
        num_candidates = request.numCandidates
        limit = request.limit

        if collection_name not in database.list_collection_names():
            raise HTTPException(
                status_code=400,
                detail=f"The collection '{collection_name}' does not exist in the database.",
            )

        collection = database[collection_name]

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
            "message": "Vector search successfully completed",
            "num_results": len(results),
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error when performing vector search: {str(e)}"
        )
