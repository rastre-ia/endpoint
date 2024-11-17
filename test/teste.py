from langchain.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import Ollama
import streamlit as st
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

uri = os.getenv("MONGODB_URI")
model_name = os.getenv("MODEL_NAME")

ollama_emb = OllamaEmbeddings(model=model_name)

client = MongoClient(uri)
db_name = "rastreia"
collection_name = "stolenitems"
collection = client[db_name][collection_name]

# Função para combinar os campos adicionais
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

# Configuração do vetor
vectorStore = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=ollama_emb,
    index_name=index_name,
    embedding_key=vector_field_name,
    text_key=text_field_name,
)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = Ollama(model=model_name, callback_manager=callback_manager)

# Streamlit Interface
def main():
    st.title("Consulta MongoDB com LLM")

    # Entrada do usuário
    query = st.text_input("Digite sua consulta:")

    retriever = vectorStore.as_retriever()  

    if st.button("Consultar"):
        with st.spinner("Consultando LLM..."):
            qa = RetrievalQA.from_chain_type(
                llm, chain_type="stuff", retriever=retriever
            )

            response = qa({"query": query})

            st.text("Resposta do LLM:")
            st.text(response["result"])

if __name__ == "__main__":
    main()
