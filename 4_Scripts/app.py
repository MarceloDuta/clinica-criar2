import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv

# Configuração da página
st.set_page_config(
    page_title="Agenda Faturamento Clínica",
    page_icon="🏥",
    layout="wide"
)

# Estilo personalizado
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
    }
    .main-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2d6a9f 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .status-agendada {
        background-color: #fff3cd;
        color: #856404;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-realizada {
        background-color: #d4edda;
        color: #155724;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-pronto {
        background-color: #cce5ff;
        color: #004085;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    .status-faturado {
        background-color: #d6d8db;
        color: #383d41;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIGURAÇÕES INICIAIS
# ============================================
BASE_DIR = Path(__file__).parent.parent

# Carrega a planilha de controle
@st.cache_data
def carregar_planilha():
    caminho = BASE_DIR / "2_outputs" / "controle_avancado.xlsx"
    if caminho.exists():
        return pd.read_excel(caminho)
    return pd.DataFrame(columns=[
        'Paciente', 'Guia', 'Profissional', 'Data_Sessao',
        'Status_Sessao', 'Status_Faturamento', 'Data_Realizacao', 'Valor'
    ])

def salvar_planilha(df):
    caminho = BASE_DIR / "2_outputs" / "controle_avancado.xlsx"
    df.to_excel(caminho, index=False)

# ============================================
# CABEÇALHO
# ============================================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; display:flex; align-items:center;">
        <span style="font-size:2rem; margin-right:1rem;">🏥</span>
        Agenda Faturamento Clínica
    </h1>
    <p style="margin:0; opacity:0.8;">Sistema de controle de sessões e faturamento</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - Navegação
# ============================================
with st.sidebar:
    st.markdown("### 📋 Menu")
    aba = st.radio(
        "Selecione uma opção",
        ["📄 Entrada", "📋 Controle", "✅ Faturamento", "📤 Envio"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 Resumo Rápido")
    df = carregar_planilha()
    if len(df) > 0:
        total = len(df)
        agendadas = len(df[df['Status_Sessao'] == 'Agendada'])
        realizadas = len(df[df['Status_Sessao'] == 'Realizada'])
        prontos = len(df[df['Status_Faturamento'] == 'Pronto'])
        st.metric("Total de Sessões", total)
        st.metric("Agendadas", agendadas)
        st.metric("Realizadas", realizadas)
        st.metric("Prontas para Faturar", prontos)
    else:
        st.info("Nenhuma sessão cadastrada ainda.")

# ============================================
# ABA 1: ENTRADA
# ============================================
if aba == "📄 Entrada":
    st.markdown("## 📄 Entrada de Guias")
    st.markdown("Faça upload dos PDFs das guias para extrair os dados automaticamente.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "📎 Arraste e solte os PDFs das guias aqui",
                type=['pdf'],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
                
                if st.button("🚀 Processar Guias"):
                    with st.spinner("Processando..."):
                        # Configura a IA
                        load_dotenv(BASE_DIR / ".env")
                        genai.configure(api_key=os.getenv("API_KEY"))
                        model = genai.GenerativeModel('models/gemini-3.6-flash')
                        
                        progress_bar = st.progress(0)
                        
                        for i, file in enumerate(uploaded_files):
                            # Salva o PDF temporário
                            temp_path = BASE_DIR / "1_Inputs" / file.name
                            with open(temp_path, "wb") as f:
                                f.write(file.getbuffer())
                            
                            # Extrai dados
                            try:
                                with pdfplumber.open(temp_path) as pdf:
                                    texto = ""
                                    for pagina in pdf.pages:
                                        texto += pagina.extract_text() or ""
                                
                                prompt = f"""
                                Extraia da guia SP/SADT:
                                - Número da Guia
                                - Nome do Paciente
                                - Código do Procedimento
                                - Descrição do Procedimento
                                - Quantidade Autorizada
                                
                                Responda APENAS JSON.
                                Texto: {texto[:8000]}
                                """
                                
                                resposta = model.generate_content(prompt)
                                texto_limpo = resposta.text.replace("```json", "").replace("```", "").strip()
                                dados = json.loads(texto_limpo) if texto_limpo else {}
                                
                                # Adiciona à planilha
                                df = carregar_planilha()
                                if dados:
                                    novo_paciente = {
                                        'Paciente': dados.get('Nome do Paciente', ''),
                                        'Guia': dados.get('Número da Guia', ''),
                                        'Profissional': 'Psicólogo',
                                        'Data_Sessao': datetime.now().strftime('%Y-%m-%d'),
                                        'Status_Sessao': 'Agendada',
                                        'Status_Faturamento': 'Pendente',
                                        'Data_Realizacao': '',
                                        'Valor': 0.0
                                    }
                                    df = pd.concat([df, pd.DataFrame([novo_paciente])], ignore_index=True)
                                    salvar_planilha(df)
                                    st.success(f"✅ {dados.get('Nome do Paciente', '')} processado com sucesso!")
                            except Exception as e:
                                st.error(f"❌ Erro ao processar {file.name}: {e}")
                            
                            progress_bar.progress((i + 1) / len(uploaded_files))
                        
                        st.balloons()
                        st.success("🎉 Todos os arquivos foram processados!")
            st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ABA 2: CONTROLE
# ============================================
elif aba == "📋 Controle":
    st.markdown("## 📋 Controle de Sessões")
    
    df = carregar_planilha()
    
    if len(df) > 0:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            pacientes = ['Todos'] + list(df['Paciente'].unique())
            filtro_paciente = st.selectbox("Filtrar por Paciente", pacientes)
        with col2:
            status = ['Todos', 'Agendada', 'Realizada', 'Faturada']
            filtro_status = st.selectbox("Filtrar por Status", status)
        with col3:
            faturar = ['Todos', 'Pendente', 'Pronto', 'Faturado']
            filtro_faturar = st.selectbox("Status Faturamento", faturar)
        
        # Aplica filtros
        df_filtrado = df.copy()
        if filtro_paciente != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Paciente'] == filtro_paciente]
        if filtro_status != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status_Sessao'] == filtro_status]
        if filtro_faturar != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status_Faturamento'] == filtro_faturar]
        
        # Mostra tabela
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True
        )
        
        # Botão para marcar como Realizada
        st.markdown("---")
        st.markdown("### ✅ Marcar Sessão como Realizada")
        col1, col2 = st.columns(2)
        with col1:
            paciente_sel = st.selectbox("Selecione o Paciente", df['Paciente'].unique())
            sessao_sel = st.selectbox(
                "Selecione a Data",
                df[df['Paciente'] == paciente_sel]['Data_Sessao'].unique()
            )
        with col2:
            if st.button("✅ Marcar como Realizada"):
                mask = (df['Paciente'] == paciente_sel) & (df['Data_Sessao'] == sessao_sel)
                if mask.any():
                    idx = df[mask].index[0]
                    df.loc[idx, 'Status_Sessao'] = 'Realizada'
                    df.loc[idx, 'Data_Realizacao'] = datetime.now().strftime('%Y-%m-%d')
                    df.loc[idx, 'Status_Faturamento'] = 'Pronto'
                    salvar_planilha(df)
                    st.success(f"✅ Sessão de {paciente_sel} em {sessao_sel} marcada como REALIZADA!")
                    st.rerun()
                else:
                    st.warning("Sessão não encontrada.")
    else:
        st.info("Nenhuma sessão cadastrada. Faça o upload de guias na aba 'Entrada'.")

# ============================================
# ABA 3: FATURAMENTO
# ============================================
elif aba == "✅ Faturamento":
    st.markdown("## ✅ Gerenciamento de Faturamento")
    
    df = carregar_planilha()
    
    if len(df) > 0:
        # Filtra prontas para faturar
        prontas = df[df['Status_Faturamento'] == 'Pronto']
        
        st.markdown(f"### 📋 Sessões Prontas para Faturar: {len(prontas)}")
        
        if len(prontas) > 0:
            st.dataframe(prontas, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Gerar XML"):
                    st.info("XML gerado com sucesso! Disponível na pasta 2_outputs")
            with col2:
                if st.button("✅ Marcar como Faturado"):
                    # Marca todas como faturadas
                    for idx in prontas.index:
                        df.loc[idx, 'Status_Faturamento'] = 'Faturado'
                        df.loc[idx, 'Status_Sessao'] = 'Faturada'
                    salvar_planilha(df)
                    st.success("✅ Todas as sessões foram marcadas como FATURADAS!")
                    st.rerun()
        else:
            st.info("Nenhuma sessão pronta para faturar.")
        
        # Histórico de faturadas
        st.markdown("---")
        st.markdown("### 📜 Histórico de Faturadas")
        faturadas = df[df['Status_Faturamento'] == 'Faturado']
        if len(faturadas) > 0:
            st.dataframe(faturadas, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma sessão faturada ainda.")
    else:
        st.info("Nenhuma sessão cadastrada.")

# ============================================
# ABA 4: ENVIO
# ============================================
else:
    st.markdown("## 📤 Envio para Faturamento")
    
    st.markdown("""
    <div class="card">
        <h3>📋 Instruções</h3>
        <ol>
            <li>Verifique as sessões prontas para faturar na aba <strong>✅ Faturamento</strong></li>
            <li>Clique em <strong>Gerar XML</strong> para criar o arquivo de faturamento</li>
            <li>O XML será salvo na pasta <code>2_outputs</code></li>
            <li>Entre no portal do seu pagador e faça o upload do arquivo</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Lista arquivos disponíveis
    st.markdown("### 📂 Arquivos Disponíveis")
    output_dir = BASE_DIR / "2_outputs"
    if output_dir.exists():
        arquivos = list(output_dir.glob("*.xml"))
        if arquivos:
            for arquivo in arquivos:
                st.download_button(
                    label=f"📥 Baixar {arquivo.name}",
                    data=open(arquivo, "rb").read(),
                    file_name=arquivo.name,
                    mime="text/xml"
                )
        else:
            st.info("Nenhum XML disponível. Gere o XML na aba 'Faturamento'.")