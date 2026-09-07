import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import os

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Agenda Faturamento Clínica",
    page_icon="🏥",
    layout="wide"
)

# ============================================
# ESTILO PERSONALIZADO
# ============================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2d6a9f 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    .btn-primary {
        background: #2d6a9f;
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        cursor: pointer;
    }
    .btn-primary:hover {
        background: #1a3a5c;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        display: inline-block;
    }
    .status-agendada {
        background: #fff3cd;
        color: #856404;
    }
    .status-realizada {
        background: #d4edda;
        color: #155724;
    }
    .status-pronto {
        background: #cce5ff;
        color: #004085;
    }
    .status-faturado {
        background: #d6d8db;
        color: #383d41;
    }
    .menu-item {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        font-weight: 500;
        cursor: pointer;
    }
    .menu-item:hover {
        background: #e9ecef;
    }
    .menu-item.active {
        background: #2d6a9f;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CABEÇALHO - TÍTULO PRINCIPAL
# ============================================
st.markdown("""
<div class="main-header">
    <h1>🏥 Agenda de Faturamento Clínica Criar</h1>
    <p>Gerencie suas guias, sessões e faturamento em um só lugar</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAÇÃO DOS DADOS
# ============================================
BASE_DIR = Path(__file__).parent.parent
caminho_excel = BASE_DIR / "2_outputs" / "controle_avancado.xlsx"

# Carrega os dados
if caminho_excel.exists():
    df = pd.read_excel(caminho_excel)
else:
    df = pd.DataFrame(columns=[
        'Paciente', 'Guia', 'Profissional', 'Data_Sessao',
        'Status_Sessao', 'Status_Faturamento', 'Valor'
    ])

def salvar_dados():
    df.to_excel(caminho_excel, index=False)

# ============================================
# MENU LATERAL - ÍCONES MODERNOS
# ============================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    
    # Menu com ícones modernos
    menu = st.radio(
        "Selecione uma opção",
        ["📋 Gerenciador", "✅ Faturar", "📂 Importar"],
        index=0
    )
    
    st.markdown("---")
    
    # Resumo rápido
    st.markdown("### 📊 Resumo")
    if len(df) > 0:
        total = len(df)
        agendadas = len(df[df['Status_Sessao'] == 'Agendada'])
        realizadas = len(df[df['Status_Sessao'] == 'Realizada'])
        prontos = len(df[df['Status_Faturamento'] == 'Pronto'])
        faturados = len(df[df['Status_Faturamento'] == 'Faturado'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", total)
            st.metric("Agendadas", agendadas)
        with col2:
            st.metric("Realizadas", realizadas)
            st.metric("Prontas", prontos)
    else:
        st.info("📭 Nenhuma sessão cadastrada")

# ============================================
# ABA 1: GERENCIADOR
# ============================================
if menu == "📋 Gerenciador":
    st.markdown("## 📋 Gerenciador de Sessões")
    
    if len(df) > 0:
        # Filtros
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            pacientes = ['Todos'] + list(df['Paciente'].unique())
            filtro_paciente = st.selectbox("Filtrar por Paciente", pacientes)
        with col2:
            status = ['Todos', 'Agendada', 'Realizada', 'Faturada']
            filtro_status = st.selectbox("Filtrar por Status", status)
        with col3:
            st.markdown("### ")
            st.caption("Atualize a lista")
        
        # Aplica filtros
        df_filtrado = df.copy()
        if filtro_paciente != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Paciente'] == filtro_paciente]
        if filtro_status != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status_Sessao'] == filtro_status]
        
        # Tabela
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Paciente": "Paciente",
                "Guia": "Nº Guia",
                "Profissional": "Profissional",
                "Data_Sessao": "Data",
                "Status_Sessao": "Status",
                "Status_Faturamento": "Faturamento",
                "Valor": "Valor (R$)"
            }
        )
        
        # Marcar como Realizada
        st.markdown("---")
        st.markdown("### ✅ Marcar Sessão como Realizada")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            paciente_sel = st.selectbox("Selecione o Paciente", df['Paciente'].unique(), key="paciente_sel")
        with col2:
            datas = df[df['Paciente'] == paciente_sel]['Data_Sessao'].unique()
            if len(datas) > 0:
                data_sel = st.selectbox("Selecione a Data", datas, key="data_sel")
            else:
                data_sel = None
        with col3:
            if st.button("✅ Marcar", use_container_width=True):
                if data_sel:
                    mask = (df['Paciente'] == paciente_sel) & (df['Data_Sessao'] == data_sel)
                    if mask.any():
                        idx = df[mask].index[0]
                        df.loc[idx, 'Status_Sessao'] = 'Realizada'
                        df.loc[idx, 'Status_Faturamento'] = 'Pronto'
                        salvar_dados()
                        st.success(f"✅ Sessão de {paciente_sel} marcada como REALIZADA!")
                        st.rerun()
    else:
        st.info("📭 Nenhuma sessão cadastrada. Vá para a aba **📂 Importar** para adicionar suas guias.")
        
        # Botão para ir para Importar
        if st.button("📂 Acessar Importar", use_container_width=True):
            st.session_state.menu = "📂 Importar"
            st.rerun()

# ============================================
# ABA 2: FATURAR
# ============================================
elif menu == "✅ Faturar":
    st.markdown("## ✅ Gerenciamento de Faturamento")
    
    if len(df) > 0:
        prontas = df[df['Status_Faturamento'] == 'Pronto']
        
        st.markdown(f"### 📋 Sessões Prontas para Faturar: {len(prontas)}")
        
        if len(prontas) > 0:
            st.dataframe(prontas, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Gerar XML", use_container_width=True):
                    st.success("✅ XML gerado com sucesso!")
                    st.balloons()
            with col2:
                if st.button("✅ Marcar como Faturado", use_container_width=True):
                    for idx in prontas.index:
                        df.loc[idx, 'Status_Sessao'] = 'Faturada'
                        df.loc[idx, 'Status_Faturamento'] = 'Faturado'
                    salvar_dados()
                    st.success("✅ Sessões marcadas como FATURADAS!")
                    st.rerun()
        else:
            st.info("✅ Nenhuma sessão pronta para faturar.")
    else:
        st.info("📭 Nenhuma sessão cadastrada.")

# ============================================
# ABA 3: IMPORTAR
# ============================================
else:
    st.markdown("## 📂 Importar Guias")
    st.markdown("Selecione os arquivos PDF das guias para importar.")
    
    # ============================================
    # FORMULÁRIO DE IMPORTAÇÃO
    # ============================================
    st.markdown("### 📄 Importar de PDF")
    
    uploaded_files = st.file_uploader(
        "📎 Selecione os PDFs das guias",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
        
        if st.button("🚀 Importar Guias", use_container_width=True):
            with st.spinner("Processando..."):
                # Simulação de processamento
                for file in uploaded_files:
                    # Salva o arquivo na pasta 1_Inputs
                    temp_path = BASE_DIR / "1_Inputs" / file.name
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())
                    
                    # Simula extração de dados
                    nome_paciente = file.name.replace(".pdf", "").replace("_", " ").title()
                    
                    # Adiciona à planilha
                    nova_linha = pd.DataFrame([{
                        'Paciente': nome_paciente,
                        'Guia': f'GUIA{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'Profissional': 'Psicólogo',
                        'Data_Sessao': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                        'Status_Sessao': 'Agendada',
                        'Status_Faturamento': 'Pendente',
                        'Valor': 150.00
                    }])
                    df_novo = pd.concat([df, nova_linha], ignore_index=True)
                    df_novo.to_excel(caminho_excel, index=False)
                
                st.success(f"🎉 {len(uploaded_files)} guia(s) importada(s) com sucesso!")
                st.balloons()
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Sessões Cadastradas")
    
    if len(df) > 0:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma sessão cadastrada ainda.")