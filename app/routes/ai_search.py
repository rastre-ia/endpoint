from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain.chains import RetrievalQA
from langchain_google_genai import GoogleGenerativeAIEmbeddings , GoogleGenerativeAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
import dotenv
import os

dotenv.load_dotenv()

uri = os.getenv("MONGODB_URI")
google_api_key = os.getenv("GOOGLE_API_KEY")  
llm_model = os.getenv("GOOGLE_MODEL")

# Conexão com o MongoDB
client = MongoClient(uri)

router = APIRouter()

# Template de prompt personalizado
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

embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  
    google_api_key=google_api_key
)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

db_name = "rastreia"
collection_name = "stolenitems"
collection = client[db_name][collection_name]


llm = GoogleGenerativeAI(
    model=llm_model,
    google_api_key=google_api_key,
    callback_manager=callback_manager,
   
)

# Função para combinar campos do documento
def combine_fields(doc):
    combined_text = " ".join(
        str(doc.get(field, "")) for field in ["object", "objectDescription", "eventDescription", "eventDate", "suspectCharacteristics"]
    )
    location = doc.get("location", {}).get("coordinates", [])
    if location and len(location) == 2:
        combined_text += f" Latitude: {location[1]}, Longitude: {location[0]}"
    return combined_text

index_name = "embeddings"
vector_field_name = "embeddings"
text_field_name = "combined_fields"

for doc in collection.find():
    combined_text = combine_fields(doc)
    collection.update_one({"_id": doc["_id"]}, {"$set": {text_field_name: combined_text}})

vectorStore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embeddings_model, 
    index_name=index_name,
    embedding_key=vector_field_name,
    text_key=text_field_name,
)

retriever = vectorStore.as_retriever()


class QueryInput(BaseModel):
    query: str

@router.post("/")
async def ai_search(data: QueryInput):
    """
    Recebe uma consulta e retorna a resposta gerada pela LLM.
    """
    try:
        # Configuração da cadeia de recuperação (RetrievalQA)
        qa = RetrievalQA.from_chain_type(
            llm,
            chain_type="stuff",
            retriever=retriever,
        )

        # Formata a consulta com o template de prompt
        formatted_query = prompt.format(query=data.query)

        # Executa a consulta
        response = qa({"query": formatted_query})

        return {
            "query": data.query,
            "response": response["result"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")