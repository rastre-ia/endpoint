from fastapi import FastAPI
from app.routes import info, image_embeddings, text_embeddings, vector_search, chat, llama_search
import os


uri = os.getenv("MONGODB_URI")


app = FastAPI()

app.include_router(info.router, prefix="/info", tags=["Info"])
app.include_router(
    image_embeddings.router, prefix="/image-embeddings", tags=["Image Embeddings"]
)
app.include_router(
    text_embeddings.router, prefix="/text-embeddings", tags=["Text Embeddings"]
)
app.include_router(
    vector_search.router, prefix="/vector-search", tags=["Vector Search"]
)

app.include_router(chat.router, prefix="/chat", tags=["Chat"])

app.include_router(llama_search.router, prefix="/llama-search", tags=["Llama Search"])

@app.get("/")
def root():
    return {"message": "Backend is running"}
