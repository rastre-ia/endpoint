from fastapi import APIRouter
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
model = os.getenv("GOOGLE_MODEL")


TEXT_EMBEDDING_DIMENSION = 768   
TEXT_EMBEDDING_MODEL = model

IMG_EMBEDDING_DIMENSION = 512  
IMG_EMBEDDING_MODEL = "ViT-B-16"


@router.get("/embedding-meta")
async def get_embedding_meta():
    """
    Retrieve the metadata of the embeddings.
    """
    return {
        "text_emb_dimension": TEXT_EMBEDDING_DIMENSION,
        "text_emb_model": TEXT_EMBEDDING_MODEL,
        "img_emb_dimension": IMG_EMBEDDING_DIMENSION,
        "img_emb_model": IMG_EMBEDDING_MODEL,
        "message": "sucess",
    }
