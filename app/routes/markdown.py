import json
import re
from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
from docling.document_converter import DocumentConverter
import os
import dotenv
from langchain_google_genai import GoogleGenerativeAI
from json import JSONDecodeError
import asyncio

dotenv.load_dotenv()

router = APIRouter()

google_api_key = os.getenv("GOOGLE_API_KEY")
llm_model = os.getenv("GOOGLE_MODEL")  

@router.post("/")
async def convert_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "O arquivo não é PDF.")
    tmp_path = None
    try:
        file_bytes = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
    
        converter = DocumentConverter()
        text_content = converter.convert(tmp_path)
        markdown = text_content.document.export_to_markdown()
        

        # Inicializa o modelo Gemini (Google Generative AI)
        gemini = GoogleGenerativeAI(model=llm_model, google_api_key=google_api_key)
        
        # Prompt para o modelo extrair os campos desejados
        prompt = f"""
        Extraia os seguintes campos do texto em Markdown e retorne um JSON:
        - object: item envolvido no crime <string>
        - objectDescription: descrição detalhada do item <string>
        - location: local do crime no formato rua,cidade,estado <string>
        - eventDate: data e hora do ocorrido no formato ISO 8601 (ex: 2025-03-13T01:22:00.000+00:00) <string>
        - eventDescription: descrição narrativa do evento <string>
        - suspectCharacteristics: características físicas e dados do suspeito <string>
        - status: classificação entre 'pending', 'on_investigation', 'solved_not_recuperated' ou 'solved_recuperated' <string>
        
        Retorne apenas o JSON válido como resposta.
        Texto:
        {markdown}
        """

        response = gemini.invoke(prompt)
        print(response)
        # Verifica se a resposta é um dicionário e contém "text"
        if isinstance(response, dict) and "text" in response:
            response_text = response["text"]
        else:
            response_text = str(response)  
        
        
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            response_text = match.group(0)
        
        try:
            extracted_data = json.loads(response_text)
        except JSONDecodeError:
            raise HTTPException(500, f"Erro ao processar a resposta do modelo. Resposta: {response_text}")
        
        return extracted_data
    
    except Exception as e:
        raise HTTPException(500, f"Erro ao processar o arquivo: {str(e)}")
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
