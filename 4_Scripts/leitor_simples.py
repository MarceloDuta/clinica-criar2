import os
import pdfplumber
import json
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

# Define a pasta principal
BASE_DIR = Path(__file__).parent.parent

# Carrega a chave API
load_dotenv(BASE_DIR / ".env")
genai.configure(api_key=os.getenv("API_KEY"))

# Lista modelos disponíveis
print("🔍 Verificando modelos disponíveis...")
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"   ✅ {model.name}")
except Exception as e:
    print(f"❌ Erro ao listar modelos: {e}")

# Usa o modelo mais básico que funciona com qualquer chave
model = genai.GenerativeModel('models/gemini-3.6-flash')
def extrair_dados_guia(caminho_pdf):
    print(f"\n📄 Lendo o PDF: {caminho_pdf}")
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() or ""
    except Exception as e:
        print(f"❌ Erro ao ler o PDF: {e}")
        return None

    if not texto_completo or len(texto_completo.strip()) < 10:
        print("⚠️ O PDF parece estar vazio ou é uma imagem (scan).")

    prompt = f"""
    Extraia do texto abaixo APENAS:
    1. O NÚMERO DA GUIA (geralmente um número com 6 a 12 dígitos).
    2. O NOME COMPLETO DO PACIENTE.
    
    Responda APENAS com um objeto JSON neste formato exato:
    {{"numero_guia": "valor", "paciente": "valor"}}
    
    Se não encontrar algum dos campos, coloque "Nao_encontrado".
    
    Texto do PDF:
    {texto_completo[:10000]}
    """
    
    try:
        resposta = model.generate_content(prompt)
        texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_limpo)
        
        print(f"✅ Dados extraídos com sucesso!")
        print(f"   🆔 Guia: {dados['numero_guia']}")
        print(f"   🧑 Paciente: {dados['paciente']}")
        return dados
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        if hasattr(e, 'response'):
            print(f"Detalhes: {e.response.text}")
        return None

if __name__ == "__main__":
    pasta_inputs = BASE_DIR / "1_Inputs"
    arquivos_pdf = list(pasta_inputs.glob("*.pdf"))
    
    if arquivos_pdf:
        caminho_teste = arquivos_pdf[0]
        print(f"\n🔍 Testando: {caminho_teste.name}\n")
        resultado = extrair_dados_guia(caminho_teste)
        if resultado:
            print("\n🎉 SISTEMA FUNCIONANDO!")
        else:
            print("\n⚠️ Verifique o arquivo .env e a chave da API.")
    else:
        print(f"⚠️ Coloque um PDF na pasta: {pasta_inputs}")