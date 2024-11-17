from langchain_ollama import OllamaEmbeddings
from langchain.vectorstores import MongoDBAtlasVectorSearch
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente
load_dotenv()

# Configuração
model_name = os.getenv("MODEL_NAME")
uri = os.getenv("MONGODB_URI")
db_name = "rastreia"
collection_name = "stolenitems"

# Inicializar o modelo de embeddings Ollama
ollama_emb = OllamaEmbeddings(model=model_name)

# Conectar ao MongoDB Atlas Vector Search
vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    uri,
    db_name + "." + collection_name,
    OllamaEmbeddings(model=model_name),
    index_name="vector_index",  # Nome do índice
)

# Realizar a busca
query = "bicicleta"
results = vector_search.similarity_search(query=query, k=3)

# Exibir resultados
for result in results:
    print(result)
