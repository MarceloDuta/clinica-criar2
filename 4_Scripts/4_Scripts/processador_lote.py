import os
import pdfplumber
import json
import time
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / ".env")
genai.configure(api_key=os.getenv("API_KEY"))

# Modelo mais rápido disponível
model = genai.GenerativeModel('models/gemini-3.6-flash')

# Controle de requisições (rate limiting)
REQUISICOES = 0
ULTIMO_REQUISICAO = time.time()

def esperar_rate_limit():
    """Controla o limite de requisições (15 por minuto)"""
    global REQUISICOES, ULTIMO_REQUISICAO
    REQUISICOES += 1
    
    # Se fez 15 requisições, espera 60 segundos
    if REQUISICOES >= 15:
        tempo_espera = 60 - (time.time() - ULTIMO_REQUISICAO)
        if tempo_espera > 0:
            print(f"⏳ Aguardando {tempo_espera:.1f}s para evitar limite...")
            time.sleep(tempo_espera)
        REQUISICOES = 0
        ULTIMO_REQUISICAO = time.time()

def extrair_67_campos_completo(caminho_pdf):
    """Extrai TODOS os 67 campos (com vazios) de forma otimizada"""
   cache_file = BASE_DIR / "2_outputs" / f"{caminho_pdf.stem}_dados.json"
    # Verifica se já foi processado
    cache_file = BASE_DIR / "2_outputs" / f"{caminho_pdf.stem}_67_campos.json"
    if cache_file.exists():
        print(f"📂 Usando cache: {caminho_pdf.name}")
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    print(f"📄 Processando: {caminho_pdf.name}")
    
    # Lê o texto do PDF
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() or ""
    except Exception as e:
        print(f"❌ Erro ao ler PDF: {e}")
        return None

    # Dicionário com TODOS os 67 campos
    campos = {f"{i}": "" for i in range(1, 68)}
    
    # Mapeamento dos campos principais (os mais comuns)
    mapeamento = {
        "1": "Registro_ANS",
        "2": "Numero_Guia_Prestador",
        "3": "Numero_Guia_Principal",
        "4": "Data_Autorizacao",
        "5": "Senha",
        "7": "Numero_Guia",
        "8": "Numero_Carteira",
        "10": "Nome_Beneficiario",
        "14": "Nome_Contratado",
        "16": "Conselho_Profissional",
        "17": "Numero_Conselho",
        "18": "UF",
        "19": "Codigo_CBO",
        "21": "Carater_Atendimento",
        "22": "Data_Solicitacao",
        "24": "Tabela",
        "25": "Codigo_Procedimento",
        "26": "Descricao_Procedimento",
        "27": "Qt_Solicitada",
        "28": "Qt_Autorizada",
        "30": "Nome_Contratado_Executante",
        "31": "Codigo_CNES",
        "32": "Tipo_Atendimento",
        "33": "Indicador_Acidente",
        "34": "Tipo_Consulta",
        "46": "Valor_Total",
        "65": "Total_Geral"
    }
    
    # Prompt otimizado (menos texto)
    prompt = f"""
    Extraia os seguintes campos da guia SP/SADT:
    
    {', '.join([f'{k}-{v}' for k, v in mapeamento.items()])}
    
    Retorne APENAS um JSON com os valores encontrados.
    Campo não encontrado = "" (vazio).
    
    Texto: {texto_completo[:8000]}
    """
    
    try:
        esperar_rate_limit()  # Controla o limite
        print("⏳ IA processando...")
        resposta = model.generate_content(prompt)
        
        texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_limpo) if texto_limpo else {}
        
        # Preenche o dicionário completo
        resultado = campos.copy()
        for chave, valor in dados.items():
            # Tenta mapear pelo número ou nome
            for num, nome in mapeamento.items():
                if chave == num or chave == nome or chave == f"{num}_{nome}":
                    resultado[num] = valor
                    break
        
        preenchidos = sum(1 for v in resultado.values() if v)
        print(f"✅ {preenchidos} campos preenchidos")
        
        # Salva cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return campos

def processar_lote():
    """Processa todos os PDFs em lote"""
    print("=" * 60)
    print("🚀 PROCESSADOR EM LOTE - 67 CAMPOS")
    print("=" * 60)
    
    pasta_inputs = BASE_DIR / "1_Inputs"
    pasta_outputs = BASE_DIR / "2_outputs"
    
    # Lista todos os PDFs
    arquivos = list(pasta_inputs.glob("*.pdf"))
    total = len(arquivos)
    
    print(f"📊 Total de arquivos: {total}")
    print(f"⏱️  Tempo estimado: ~{total * 3} segundos\n")
    
    resultados = {}
    for i, arquivo in enumerate(arquivos, 1):
        print(f"\n[{i}/{total}]", end=" ")
        resultados[arquivo.name] = extrair_67_campos_completo(arquivo)
    
    # Salva relatório consolidado
    relatorio = {
        "data_processamento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_arquivos": total,
        "arquivos": resultados
    }
    
    with open(pasta_outputs / "relatorio_completo.json", 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print(f"📁 Relatório salvo em: {pasta_outputs / 'relatorio_completo.json'}")
    print("=" * 60)

if __name__ == "__main__":
    processar_lote()