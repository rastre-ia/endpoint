from fastapi import APIRouter


router = APIRouter()

TEXT_EMBEDDING_DIMENSION = 2048
TEXT_EMBEDDING_MODEL = "llama3.2:1b"

IMG_EMBEDDING_DIMENSION = 512  # não sabo o valor correto
IMG_EMBEDDING_MODEL = "ViT-B-16"


@router.get("/embedding-meta")
async def get_embedding_meta():
    """
    Retorna os metadados dos embeddings de imagem e texto.
    """
    return {
        "text_emb_dimension": TEXT_EMBEDDING_DIMENSION,
        "text_emb_model": TEXT_EMBEDDING_MODEL,
        "img_emb_dimension": IMG_EMBEDDING_DIMENSION,
        "img_emb_model": IMG_EMBEDDING_MODEL,
        "message": "sucess",
    }
