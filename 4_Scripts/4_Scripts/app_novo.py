import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Agenda Faturamento Clínica",
    page_icon="🏥",
    layout="wide"
)

# CABEÇALHO
st.title("🏥 Agenda Faturamento Clínica")
st.markdown("---")

# SIDEBAR - Menu
with st.sidebar:
    st.markdown("### 📋 Menu")
    aba = st.radio(
        "Selecione uma opção",
        ["📋 Controle", "✅ Faturamento", "📄 Importar"],
        index=0
    )
    st.markdown("---")
    
    # Carrega os dados
    BASE_DIR = Path(__file__).parent.parent
    caminho = BASE_DIR / "2_outputs" / "controle_avancado.xlsx"
    
    if caminho.exists():
        df = pd.read_excel(caminho)
    else:
        df = pd.DataFrame(columns=[
            'Paciente', 'Guia', 'Profissional', 'Data_Sessao',
            'Status_Sessao', 'Status_Faturamento', 'Valor'
        ])
    
    # Resumo rápido
    st.markdown("### 📊 Resumo")
    if len(df) > 0:
        st.metric("Total de Sessões", len(df))
        st.metric("Agendadas", len(df[df['Status_Sessao'] == 'Agendada']))
        st.metric("Realizadas", len(df[df['Status_Sessao'] == 'Realizada']))
        st.metric("Prontas para Faturar", len(df[df['Status_Faturamento'] == 'Pronto']))
    else:
        st.info("📭 Nenhuma sessão cadastrada")

# ============================================
# ABA 1: CONTROLE
# ============================================
if aba == "📋 Controle":
    st.markdown("## 📋 Controle de Sessões")
    
    if len(df) > 0:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            pacientes = ['Todos'] + list(df['Paciente'].unique())
            filtro_paciente = st.selectbox("Paciente", pacientes)
        with col2:
            status = ['Todos', 'Agendada', 'Realizada', 'Faturada']
            filtro_status = st.selectbox("Status", status)
        
        # Aplica filtros
        df_filtrado = df.copy()
        if filtro_paciente != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Paciente'] == filtro_paciente]
        if filtro_status != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status_Sessao'] == filtro_status]
        
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
        
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
                        df.to_excel(caminho, index=False)
                        st.success(f"✅ Sessão de {paciente_sel} em {data_sel} marcada como REALIZADA!")
                        st.rerun()
    else:
        st.info("📭 Nenhuma sessão cadastrada. Vá para a aba '📄 Importar' para adicionar.")

# ============================================
# ABA 2: FATURAMENTO
# ============================================
elif aba == "✅ Faturamento":
    st.markdown("## ✅ Faturamento")
    
    if len(df) > 0:
        # Filtra prontas
        prontas = df[df['Status_Faturamento'] == 'Pronto']
        
        st.markdown(f"### 📋 Sessões Prontas para Faturar: {len(prontas)}")
        
        if len(prontas) > 0:
            st.dataframe(prontas, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Gerar XML", use_container_width=True):
                    st.success("✅ XML gerado com sucesso! Veja na pasta 2_outputs")
                    st.balloons()
            with col2:
                if st.button("✅ Marcar como Faturado", use_container_width=True):
                    for idx in prontas.index:
                        df.loc[idx, 'Status_Sessao'] = 'Faturada'
                        df.loc[idx, 'Status_Faturamento'] = 'Faturado'
                    df.to_excel(caminho, index=False)
                    st.success("✅ Todas as sessões marcadas como FATURADAS!")
                    st.rerun()
        else:
            st.info("✅ Nenhuma sessão pronta para faturar no momento.")
    else:
        st.info("📭 Nenhuma sessão cadastrada.")

# ============================================
# ABA 3: IMPORTAR
# ============================================
else:
    st.markdown("## 📄 Importar Dados")
    st.markdown("Use esta aba para adicionar sessões manualmente.")
    
    with st.form("form_importar"):
        col1, col2 = st.columns(2)
        with col1:
            novo_paciente = st.text_input("Nome do Paciente", placeholder="Ex: João Silva")
            nova_guia = st.text_input("Número da Guia", placeholder="Ex: 123456789")
            novo_profissional = st.selectbox("Profissional", ["Psicólogo", "Fonoaudiólogo", "Fisioterapeuta", "Terapeuta Ocupacional"])
        with col2:
            nova_data = st.date_input("Data da Sessão", datetime.now())
            novo_valor = st.number_input("Valor (R$)", min_value=0.0, value=150.0)
        
        submitted = st.form_submit_button("➕ Adicionar Sessão")
        
        if submitted:
            if novo_paciente and nova_guia:
                nova_linha = pd.DataFrame([{
                    'Paciente': novo_paciente,
                    'Guia': nova_guia,
                    'Profissional': novo_profissional,
                    'Data_Sessao': nova_data.strftime('%Y-%m-%d'),
                    'Status_Sessao': 'Agendada',
                    'Status_Faturamento': 'Pendente',
                    'Valor': novo_valor
                }])
                df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_excel(caminho, index=False)
                st.success(f"✅ Sessão de {novo_paciente} adicionada com sucesso!")
                st.rerun()
            else:
                st.warning("⚠️ Preencha o nome do paciente e o número da guia.")
    
    st.markdown("---")
    st.markdown("### 📋 Dados Atuais")
    if len(df) > 0:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado cadastrado ainda.")