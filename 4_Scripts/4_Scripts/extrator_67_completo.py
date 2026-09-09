import os
import pdfplumber
import json
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / ".env")
genai.configure(api_key=os.getenv("API_KEY"))

# Modelo rápido
model = genai.GenerativeModel('models/gemini-3.6-flash')
def extrair_67_campos_completo(caminho_pdf):
    """
    Extrai TODOS os 67 campos da guia SP/SADT.
    Campos não preenchidos retornam como "" (vazio).
    """
    print(f"\n📄 Lendo: {caminho_pdf.name}")
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() or ""
    except Exception as e:
        print(f"❌ Erro ao ler PDF: {e}")
        return None

    # Dicionário com TODOS os 67 campos da guia SP/SADT
    campos_67 = {
        "1_Registro_ANS": "",
        "2_Numero_Guia_Prestador": "",
        "3_Numero_Guia_Principal": "",
        "4_Data_Autorizacao": "",
        "5_Senha": "",
        "6_Data_Validade_Senha": "",
        "7_Numero_Guia": "",
        "8_Numero_Carteira": "",
        "9_Validade_Carteira": "",
        "10_Nome_Beneficiario": "",
        "11_Codigo_Plano": "",
        "12_Atendimento_RN": "",
        "13_Codigo_Operadora": "",
        "14_Nome_Contratado": "",
        "15_Nome_Profissional_Solicitante": "",
        "16_Conselho_Profissional": "",
        "17_Numero_Conselho": "",
        "18_UF": "",
        "19_Codigo_CBO": "",
        "20_Assinatura_Profissional_Solicitante": "",
        "21_Carater_Atendimento": "",
        "22_Data_Solicitacao": "",
        "23_Indicacao_Clinica": "",
        "24_Tabela": "",
        "25_Codigo_Procedimento": "",
        "26_Descricao_Procedimento": "",
        "27_Qt_Solicitada": "",
        "28_Qt_Autorizada": "",
        "29_Codigo_Operadora_Executante": "",
        "30_Nome_Contratado_Executante": "",
        "31_Codigo_CNES": "",
        "32_Tipo_Atendimento": "",
        "33_Indicador_Acidente": "",
        "34_Tipo_Consulta": "",
        "35_Motivo_Encerramento": "",
        "36_Data_Execucao": "",
        "37_Hora_Inicial": "",
        "38_Hora_Final": "",
        "39_Tabela_Execucao": "",
        "40_Codigo_Procedimento_Executado": "",
        "41_Descricao_Procedimento_Executado": "",
        "42_Quantidade": "",
        "43_Via": "",
        "44_Tecnica": "",
        "45_Fator_Reducao_Acrescimo": "",
        "46_Valor_Total": "",
        "47_Assinatura_Responsavel": "",
        "48_Seq_Ref": "",
        "49_Grau_Participacao": "",
        "50_Codigo_Operadora_CPF": "",
        "51_Nome_Profissional_Executante": "",
        "52_Conselho_Profissional_Executante": "",
        "53_Numero_Conselho_Executante": "",
        "54_UF_Executante": "",
        "55_Codigo_CBO_Executante": "",
        "56_Data_Realizacao_Procedimentos_Serie": "",
        "57_Assinatura_Beneficiario": "",
        "58_Observacao_Justificativa": "",
        "59_Total_Procedimentos": "",
        "60_Total_Taxas_Alugueis": "",
        "61_Total_Materiais": "",
        "62_Total_OPME": "",
        "63_Total_Medicamentos": "",
        "64_Total_Gases_Medicinais": "",
        "65_Total_Geral": "",
        "66_Assinatura_Responsavel_Autorizacao": "",
        "67_Assinatura_Contratado": ""
    }

    # Prompt otimizado
    prompt = f"""
    Extraia os valores dos campos da guia SP/SADT.
    Use os NÚMEROS dos campos para identificar cada um.
    
    Retorne APENAS um JSON com os campos encontrados.
    NÃO inclua campos vazios.
    
    Exemplo de resposta:
    {{"1_Registro_ANS": "346659", "10_Nome_Beneficiario": "ICARO GLUCK"}}
    
    Texto da guia:
    {texto_completo[:15000]}
    """
    
    try:
        print("⏳ Extraindo campos...")
        resposta = model.generate_content(prompt)
        texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
        
        if not texto_limpo:
            print("⚠️ IA não retornou dados.")
            return campos_67
        
        dados_encontrados = json.loads(texto_limpo)
        
        # Preenche os campos encontrados no dicionário completo
        for chave, valor in dados_encontrados.items():
            if chave in campos_67:
                campos_67[chave] = valor
        
        # Conta quantos campos foram preenchidos
        preenchidos = sum(1 for v in campos_67.values() if v)
        
        print(f"✅ {preenchidos} campos preenchidos encontrados (de 67)")
        print("=" * 60)
        
        # Mostra APENAS os campos preenchidos (para não poluir)
        for chave, valor in campos_67.items():
            if valor:
                print(f"   {chave}: {valor}")
        
        print("=" * 60)
        print(f"   Campos vazios: {67 - preenchidos}")
        
        return campos_67
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return campos_67

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 EXTRATOR DOS 67 CAMPOS (COMPLETO)")
    print("=" * 60)
    
    pasta_inputs = BASE_DIR / "1_Inputs"
    arquivos_pdf = list(pasta_inputs.glob("*.pdf"))
    
    if arquivos_pdf:
        for arquivo in arquivos_pdf:
            resultado = extrair_67_campos_completo(arquivo)
            if resultado:
                # Salva o JSON completo (com todos os 67 campos)
                caminho_json = BASE_DIR / "2_outputs" / f"{arquivo.stem}_67_campos.json"
                with open(caminho_json, 'w', encoding='utf-8') as f:
                    json.dump(resultado, f, ensure_ascii=False, indent=2)
                print(f"💾 Dados completos salvos em: {caminho_json}")
                
                # Mostra quantos campos estão vazios
                vazios = [k for k, v in resultado.items() if not v]
                print(f"📊 Campos vazios: {len(vazios)}")
                if vazios:
                    print(f"   Exemplo: {', '.join(vazios[:5])}...")
                
                print(f"\n🎉 Extração completa!\n")
    else:
        print("⚠️ Coloque um PDF na pasta 1_Inputs")