from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image
import requests
from io import BytesIO
from langchain_experimental.open_clip import OpenCLIPEmbeddings

clip_embd = OpenCLIPEmbeddings(model_name="ViT-B-16", checkpoint="laion2b_s34b_b88k")

router = APIRouter()


class ImageInput(BaseModel):
    url: str


@router.post("/")
async def generate_image_embeddings(data: ImageInput):
    """
    Recebe uma URL de imagem e retorna os embeddings gerados.
    """
    try:
        response = requests.get(data.url)
        response.raise_for_status()  # Verifica se a URL é válida
        image = Image.open(BytesIO(response.content)).convert("RGB")
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=400, detail=f"Erro ao carregar a imagem da URL: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Erro ao processar a imagem: {str(e)}"
        )

    # Converta a imagem para um fluxo de bytes
    with BytesIO() as img_byte_arr:
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)  # Voltar para o início do fluxo

        try:
            embeddings = clip_embd.embed_image([img_byte_arr])  # Passe o fluxo de bytes
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao gerar embeddings: {str(e)}"
            )

    return {
        "embeddings": embeddings[0],
        "dimension": len(embeddings[0]),
        "message": "Embeddings gerados com sucesso",
    }
