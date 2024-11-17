from typing import Any, Dict, Sequence, Optional
from fastapi import APIRouter, HTTPException
import ollama
from dotenv import load_dotenv
import os
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ollama._types import Options, Message

load_dotenv()
model_name = os.getenv("MODEL_NAME")
router = APIRouter()


@router.post("/")
async def chat(payload: Dict[Any, Any]):
    """
    Receives a text and generates embeddings for it.
    """
    messages = payload.get("messages")
    options = payload.get("options")

    try:
        response = ollama.chat(model=model_name, messages=messages, options=options)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in generating: {str(e)}")
