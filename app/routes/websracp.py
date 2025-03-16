from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import json
import re
from langchain_google_genai import GoogleGenerativeAI
import dotenv
import os
from fake_useragent import UserAgent  

dotenv.load_dotenv()

router = APIRouter()
google_api_key = os.getenv("GOOGLE_API_KEY")
llm_model = os.getenv("GOOGLE_MODEL")

ua = UserAgent()  

class Query(BaseModel):
    search_term: str

def parse_gemini_response(response: str) -> list:
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("Resposta do Gemini não contém JSON válido")

@router.post("/")
async def parse_listings(query: Query):
    
    jina_url = f"https://r.jina.ai/https://www.olx.com.br/brasil?q={query.search_term}&sf=1"

    headers = {
        "User-Agent": ua.random,  
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.olx.com.br/",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(jina_url, headers=headers, timeout=60)
        response.raise_for_status()
        markdown_content = response.text[:9000]  
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Erro ao buscar dados: {str(e)}")

    # Configurar prompt para o Gemini
    prompt_template = """Analise o seguinte Markdown de listagens de TODOS os produtos e extraia :
    - Título do anúncio
    - Localização
    - URL da primeira imagem
    - URL do produto
    Retorne APENAS um array JSON com objetos contendo: title, location, img_url, product_url.
    
    Conteúdo:
    {content}"""

    llm = GoogleGenerativeAI(model=llm_model, google_api_key=google_api_key, temperature=0)

    try:
        result = llm.invoke(prompt_template.format(content=markdown_content))
        
        parsed_data = parse_gemini_response(result)
        
        if not isinstance(parsed_data, list):
            raise ValueError("Formato inválido na resposta")
            
        for item in parsed_data:
            if not all(key in item for key in ['title', 'location', 'img_url','product_url']):
                raise ValueError("Itens incompletos na resposta")
        return {"results": parsed_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
