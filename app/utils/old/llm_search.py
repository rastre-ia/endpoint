from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from langchain.vectorstores import MongoDBAtlasVectorSearch
from langchain.chains import RetrievalQA
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGODB_URI")
model_name = os.getenv("GOOGLE_MODEL")
client = MongoClient(uri)

router = APIRouter()

custom_prompt_template = """
Comece sempre com "Olá policial" no início de cada resposta.
Você é um assistente especializado utilizado por policiais para fornecer dados detalhados sobre ocorrências policiais. 
Suas respostas devem ser claras, objetivas e didáticas, priorizando a relevância e o contexto da situação.
Se houver itens roubados, forneça uma lista detalhada, incluindo:
1. Descrição do item;
2. Data do ocorrido;
3. Características do suspeito, caso disponíveis.
4. Latitude e longitude do local do crime.
Utilize marcadores ou numeração para organizar as informações de forma legível. Evite repetir dados já fornecidos anteriormente e exclua qualquer informação irrelevante. 
Não repita consultas anteriores.
Só forneça informações relevantes.
Use apenas dados que tenham o objeto de interesse.
Pergunta: {query}
"""

prompt = PromptTemplate(template=custom_prompt_template, input_variables=["query"])

ollama_emb = OllamaEmbeddings(model=model_name)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


db_name = "rastreia"
collection_name = "stolenitems"
collection = client[db_name][collection_name]


llm = Ollama(
    model=model_name,
    callback_manager=callback_manager,
)



def combine_fields(doc):
    combined_text = " ".join(
        str(doc.get(field, "")) for field in ["object", "objectDescription", "eventDescription", "eventDate", "suspectCharacteristics"]
    )
    location = doc.get("location", {}).get("coordinates", [])
    if location and len(location) == 2:
        combined_text += f" Latitude: {location[1]}, Longitude: {location[0]}"
    return combined_text


index_name = "vector_index"
vector_field_name = "embeddings"
text_field_name = "combined_fields"

for doc in collection.find():
    combined_text = combine_fields(doc)
    collection.update_one({"_id": doc["_id"]}, {"$set": {text_field_name: combined_text}})

vectorStore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=ollama_emb,
    index_name=index_name,
    embedding_key=vector_field_name,
    text_key=text_field_name,
)

retriever = vectorStore.as_retriever()

class QueryInput(BaseModel):
    query: str


@router.post("/")
async def llama_search(data: QueryInput):
    """
    Recebe uma consulta e retorna a resposta gerada pela LLM.
    """
    try:


        qa = RetrievalQA.from_chain_type(llm, 
                                         chain_type="stuff", 
                                         retriever=retriever,
                                         )
        response = qa({ "query": prompt.format(query=data.query), })
        return {
            "query": data.query,
            "response": response["result"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")