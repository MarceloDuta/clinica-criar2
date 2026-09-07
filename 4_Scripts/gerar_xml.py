import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber

BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / ".env")
genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel('models/gemini-3.6-flash')

def extrair_todos_dados(caminho_pdf):
    """Extrai todos os campos do PDF"""
    print(f"📄 Lendo: {caminho_pdf.name}")
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() or ""
    except Exception as e:
        print(f"❌ Erro ao ler PDF: {e}")
        return None

    prompt = f"""
    Extraia do texto abaixo os seguintes campos da guia SP/SADT:
    
    1. numero_guia
    2. paciente
    3. codigo_procedimento
    4. descricao_procedimento
    5. quantidade_autorizada
    6. data_autorizacao
    7. numero_carteira
    8. validade_carteira
    9. registro_ans
    10. nome_contratado
    11. valor_total
    12. guia_principal
    
    Responda APENAS com JSON neste formato:
    {{
        "numero_guia": "valor",
        "paciente": "valor",
        "codigo_procedimento": "valor",
        "descricao_procedimento": "valor",
        "quantidade_autorizada": "valor",
        "data_autorizacao": "valor",
        "numero_carteira": "valor",
        "validade_carteira": "valor",
        "registro_ans": "valor",
        "nome_contratado": "valor",
        "valor_total": "valor",
        "guia_principal": "valor"
    }}
    
    Texto: {texto_completo[:15000]}
    """
    
    try:
        resposta = model.generate_content(prompt)
        texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_limpo)
        return dados
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def gerar_xml_tiss(dados, nome_arquivo="faturamento.xml"):
    """Gera um arquivo XML no formato TISS"""
    
    # Cria o elemento raiz
    root = ET.Element("tiss:mensagemTISS", {
        "xmlns:tiss": "http://www.ans.gov.br/padroes/tiss/schemas",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "versao": "4.01.00"
    })
    
    # Cria o cabeçalho
    cabecalho = ET.SubElement(root, "tiss:cabecalho")
    ET.SubElement(cabecalho, "tiss:identificacaoTransacao").text = "1"
    ET.SubElement(cabecalho, "tiss:dataRegistro").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    ET.SubElement(cabecalho, "tiss:horaRegistro").text = datetime.now().strftime("%H:%M:%S")
    
    # Cria a guia SP/SADT
    guia = ET.SubElement(root, "tiss:guiaSP_SADT")
    ET.SubElement(guia, "tiss:numeroGuia").text = dados.get('numero_guia', '')
    ET.SubElement(guia, "tiss:guiaPrincipal").text = dados.get('guia_principal', '')
    
    # Dados do Beneficiário
    dados_beneficiario = ET.SubElement(guia, "tiss:dadosBeneficiario")
    ET.SubElement(dados_beneficiario, "tiss:numeroCarteira").text = dados.get('numero_carteira', '')
    ET.SubElement(dados_beneficiario, "tiss:nome").text = dados.get('paciente', '')
    
    # Dados do Contratado Executante
    contratado = ET.SubElement(guia, "tiss:dadosContratadoExecutante")
    ET.SubElement(contratado, "tiss:nome").text = dados.get('nome_contratado', '')
    ET.SubElement(contratado, "tiss:registroANS").text = dados.get('registro_ans', '')
    
    # Procedimento
    procedimentos = ET.SubElement(guia, "tiss:procedimentosExecutados")
    procedimento = ET.SubElement(procedimentos, "tiss:procedimento")
    ET.SubElement(procedimento, "tiss:codigoProcedimento").text = dados.get('codigo_procedimento', '')
    ET.SubElement(procedimento, "tiss:descricaoProcedimento").text = dados.get('descricao_procedimento', '')
    ET.SubElement(procedimento, "tiss:quantidade").text = dados.get('quantidade_autorizada', '')
    ET.SubElement(procedimento, "tiss:dataRealizacao").text = dados.get('data_autorizacao', '')
    
    # Gera o XML com formatação bonita
    xml_string = ET.tostring(root, encoding='utf-8', method='xml')
    dom = minidom.parseString(xml_string)
    xml_formatado = dom.toprettyxml(indent="  ")
    
    # Salva o arquivo
    caminho_arquivo = BASE_DIR / "2_outputs" / nome_arquivo
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        f.write(xml_formatado)
    
    print(f"✅ XML salvo em: {caminho_arquivo}")
    return caminho_arquivo

if __name__ == "__main__":
    print("=" * 50)
    print("📋 GERADOR DE XML TISS")
    print("=" * 50)
    
    pasta_inputs = BASE_DIR / "1_Inputs"
    arquivos_pdf = list(pasta_inputs.glob("*.pdf"))
    
    if arquivos_pdf:
        for arquivo in arquivos_pdf:
            dados = extrair_todos_dados(arquivo)
            if dados:
                print("\n📊 Dados extraídos:")
                print("=" * 50)
                for chave, valor in dados.items():
                    print(f"   {chave}: {valor}")
                print("=" * 50)
                
                # Gera o XML
                gerar_xml_tiss(dados)
                print("\n🎉 XML TISS gerado com sucesso!")
    else:
        print("⚠️ Coloque um PDF na pasta 1_Inputs")