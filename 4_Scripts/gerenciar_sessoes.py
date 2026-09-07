import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import json
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber

# Define a pasta principal
BASE_DIR = Path(__file__).parent.parent

# Carrega a chave API
load_dotenv(BASE_DIR / ".env")
genai.configure(api_key=os.getenv("API_KEY"))

# Usa o modelo que funcionou
model = genai.GenerativeModel('models/gemini-3.6-flash')

# --- FUNÇÃO 1: Extrair dados do PDF ---
def extrair_dados_guia(caminho_pdf):
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
    Extraia do texto abaixo APENAS:
    1. O NÚMERO DA GUIA.
    2. O NOME COMPLETO DO PACIENTE.
    
    Responda APENAS com um JSON:
    {{"numero_guia": "valor", "paciente": "valor"}}
    
    Texto: {texto_completo[:10000]}
    """
    
    try:
        resposta = model.generate_content(prompt)
        texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
        dados = json.loads(texto_limpo)
        return dados
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return None

# --- FUNÇÃO 2: Agendar sessões ---
def agendar_sessoes(dados_paciente, num_sessoes=10, dias_semana=[0,1,2,3,4]):
    """
    Agenda sessões para um paciente.
    dias_semana: 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta
    """
    paciente = dados_paciente['paciente']
    guia = dados_paciente['numero_guia']
    
    print(f"📅 Agendando {num_sessoes} sessões para {paciente}")
    
    # Lista para armazenar as sessões
    sessoes = []
    
    # Data de início: amanhã
    data_atual = datetime.now() + timedelta(days=1)
    
    # Conta quantas sessões foram agendadas
    contador = 0
    
    while contador < num_sessoes:
        # Verifica se o dia da semana está na lista permitida
        if data_atual.weekday() in dias_semana:
            sessoes.append({
                'Paciente': paciente,
                'Guia': guia,
                'Data_Sessao': data_atual.strftime('%Y-%m-%d'),
                'Status': 'Agendada'
            })
            contador += 1
        
        # Avança para o próximo dia
        data_atual += timedelta(days=1)
    
    return sessoes

# --- FUNÇÃO 3: Salvar em Excel ---
def salvar_planilha(sessoes, nome_arquivo="controle_sessoes.xlsx"):
    """Salva a lista de sessões em um arquivo Excel"""
    
    # Cria um DataFrame do Pandas
    df = pd.DataFrame(sessoes)
    
    # Caminho completo do arquivo
    caminho_arquivo = BASE_DIR / "2_outputs" / nome_arquivo
    
    # Salva como Excel
    df.to_excel(caminho_arquivo, index=False)
    
    print(f"✅ Planilha salva em: {caminho_arquivo}")
    return caminho_arquivo

# --- FUNÇÃO 4: Carregar planilha existente ---
def carregar_planilha(nome_arquivo="controle_sessoes.xlsx"):
    """Carrega uma planilha existente"""
    caminho_arquivo = BASE_DIR / "2_outputs" / nome_arquivo
    
    if caminho_arquivo.exists():
        df = pd.read_excel(caminho_arquivo)
        print(f"📂 Planilha carregada: {len(df)} sessões")
        return df
    else:
        print("⚠️ Planilha não encontrada. Criando nova...")
        return pd.DataFrame(columns=['Paciente', 'Guia', 'Data_Sessao', 'Status'])

# --- FUNÇÃO 5: Marcar sessão como pronta ---
def marcar_pronta(df, paciente, guia):
    """Marca a primeira sessão 'Agendada' como 'Pronta' para um paciente"""
    
    # Filtra as sessões agendadas para este paciente/guia
    mask = (df['Paciente'] == paciente) & (df['Guia'] == guia) & (df['Status'] == 'Agendada')
    
    if mask.any():
        # Pega o índice da primeira sessão agendada
        idx = df[mask].index[0]
        df.loc[idx, 'Status'] = 'Pronta'
        print(f"✅ Sessão de {paciente} marcada como PRONTA!")
        return df
    else:
        print(f"⚠️ Nenhuma sessão agendada encontrada para {paciente}")
        return df

# --- FUNÇÃO 6: Mostrar resumo ---
def mostrar_resumo(df):
    """Mostra um resumo das sessões"""
    print("\n📊 RESUMO DAS SESSÕES:")
    print(f"   Total: {len(df)}")
    
    if len(df) > 0:
        agendadas = len(df[df['Status'] == 'Agendada'])
        prontas = len(df[df['Status'] == 'Pronta'])
        print(f"   Agendadas: {agendadas}")
        print(f"   Prontas: {prontas}")
        
        # Mostra os pacientes
        pacientes = df['Paciente'].unique()
        print(f"   Pacientes: {', '.join(pacientes)}")

# ============================================
# EXECUÇÃO PRINCIPAL (quando rodar o script)
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("🏥 SISTEMA DE GERENCIAMENTO DE SESSÕES")
    print("=" * 50)
    
    # 1. Carrega a planilha existente (se houver)
    df = carregar_planilha()
    
    # 2. Procura por novos PDFs
    pasta_inputs = BASE_DIR / "1_Inputs"
    arquivos_pdf = list(pasta_inputs.glob("*.pdf"))
    
    novos_pacientes = 0
    
    for arquivo in arquivos_pdf:
        # Verifica se este PDF já foi processado (pelo número da guia)
        dados = extrair_dados_guia(arquivo)
        
        if dados:
            guia = dados['numero_guia']
            # Verifica se a guia já existe na planilha
            if guia not in df['Guia'].values:
                print(f"🆕 Novo paciente: {dados['paciente']}")
                
                # Agenda 10 sessões
                sessoes = agendar_sessoes(dados, num_sessoes=10)
                
                # Adiciona à planilha
                df_novas = pd.DataFrame(sessoes)
                df = pd.concat([df, df_novas], ignore_index=True)
                novos_pacientes += 1
            else:
                print(f"⏩ Guia {guia} já está na planilha.")
    
    # 3. Salva a planilha atualizada
    if novos_pacientes > 0:
        salvar_planilha(df)
    
    # 4. Mostra resumo
    mostrar_resumo(df)
    
    print("\n" + "=" * 50)
    print("✅ Sistema finalizado!")
    print("=" * 50)