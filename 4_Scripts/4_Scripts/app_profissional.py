import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta

# ============================================
# INICIALIZAÇÃO DOS DADOS
# ============================================
BASE_DIR = Path(__file__).parent.parent
caminho_excel = BASE_DIR / "2_outputs" / "controle_avancado.xlsx"
caminho_pacientes = BASE_DIR / "2_outputs" / "pacientes.json"
caminho_profissionais = BASE_DIR / "2_outputs" / "profissionais.json"

# Valores padrão (procedimentos)
VALORES_PADRAO = {
    "00081020016": {"procedimento": "PSICOTERAPIA PELO METODO DE ANALISA ABA", "valor": 84.88},
    "0081020023": {"procedimento": "PSICOPEDAGOGIA", "valor": 36.82},
    "0081030010": {"procedimento": "PSICOMOTRICIDADE", "valor": 36.82},
    "0081030037": {"procedimento": "PSICOTERAPIA INDIVIDUAL", "valor": 62.62},
    "0081040024": {"procedimento": "FONOAUDIOLOGIA", "valor": 62.62},
    "50000012": {"procedimento": "PSICOMOTRICIDADE INDIVIDUAL", "valor": 36.82},
    "50000080": {"procedimento": "TERAPIA OCUPACIONAL", "valor": 54.79},
    "50000470": {"procedimento": "PSICOTERAPIA INDIVIDUAL", "valor": 62.62},
    "50000616": {"procedimento": "FONOAUDIOLOGIA", "valor": 62.62},
    "60401201": {"procedimento": "PSICOTERAPIA PELO METODO DE ANALISA ABA", "valor": 77.57},
}

caminho_valores = BASE_DIR / "2_outputs" / "tabela_valores.json"

def carregar_valores():
    if caminho_valores.exists():
        with open(caminho_valores, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return VALORES_PADRAO.copy()

def salvar_valores(nova_tabela):
    with open(caminho_valores, "w", encoding="utf-8") as f:
        json.dump(nova_tabela, f, indent=4, ensure_ascii=False)

TABELA_VALORES = carregar_valores()

def carregar_pacientes():
    if caminho_pacientes.exists():
        with open(caminho_pacientes, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def salvar_pacientes(pacientes):
    with open(caminho_pacientes, "w", encoding="utf-8") as f:
        json.dump(pacientes, f, indent=4, ensure_ascii=False)

def carregar_profissionais():
    if caminho_profissionais.exists():
        with open(caminho_profissionais, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def salvar_profissionais(profissionais):
    with open(caminho_profissionais, "w", encoding="utf-8") as f:
        json.dump(profissionais, f, indent=4, ensure_ascii=False)

if caminho_excel.exists():
    df = pd.read_excel(caminho_excel)
else:
    df = pd.DataFrame(columns=['Paciente', 'Guia', 'Profissional', 'Data_Sessao', 'Horario_Sessao', 'Status_Sessao', 'Status_Faturamento', 'Valor'])

def salvar_dados():
    df.to_excel(caminho_excel, index=False)

def formatar_datas(df_view):
    if 'Data_Sessao' in df_view.columns and len(df_view) > 0:
        df_view['Data_Sessao'] = pd.to_datetime(df_view['Data_Sessao'], errors='coerce').dt.strftime('%d/%m/%Y')
    return df_view

def formatar_moeda(valor):
    return f"R$ {valor:.2f}"

# ============================================
# FUNÇÃO PARA RENDERIZAR A GUIA (MODO PAISAGEM)
# ============================================
def render_guia_cassi(d):
    html = f"""
    <div style="font-family: Arial, sans-serif; width: 100%; max-width: 1300px; background: #fff; border: 2px solid #000; margin: 0 auto; font-size: 12px;">
        <!-- Cabeçalho -->
        <div style="display: flex; justify-content: space-between; padding: 5px; border-bottom: 2px solid #000;">
            <div style="font-weight: bold; font-size: 24px; color: #0056b3;">CASSI</div>
            <div style="text-align: center; font-weight: bold; font-size: 16px;">GUIA DE SERVIÇO PROFISSIONAL / SERVIÇO AUXILIAR DE<br>DIAGNÓSTICO E TERAPIA - SP/SADT</div>
            <div style="text-align: right;">
                <div style="font-size: 11px;">2 - Nº Guia no Prestador</div>
                <div style="font-weight: bold; font-size: 18px;">{d['guia_prestador']}</div>
                <div style="border: 1px solid #000; width: 100px; height: 30px; background: repeating-linear-gradient(90deg, #000 0, #000 2px, #fff 2px, #fff 4px);"></div>
            </div>
        </div>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #000;">
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>1 - Nº Guia Prestador</b><br>{d['guia_prestador']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>2 - Nº Guia Principal</b><br>{d['guia_principal']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>3 - Nº Guia Operadora</b><br>{d['guia_operadora']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>4 - Data Autorização</b><br>{d['data_autorizacao']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>5 - Senha</b><br>{d['senha']}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>6 - Validade Senha</b><br>{d['validade_senha']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>7 - Nº Guia Atribuído Operadora</b><br>{d['guia_operadora']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>8 - Carteirinha</b><br>{d['carteirinha']}</td>
                <td style="border: 1px solid #000; padding: 3px;"></td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados do Beneficiário</td></tr>
            <tr>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>9 - Nome</b><br>{d['nome_beneficiario']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>10 - Validade Carteira</b><br>{d['validade_carteira']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>11 - Atendimento a RN</b><br>{d['atendimento_rn']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados do Solicitante</td></tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>12 - Código Operadora</b><br>{d['codigo_operadora']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>13 - Nome Contratado</b><br>{d['nome_contratado']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>14 - Nome Prof. Solicitante</b><br>{d['nome_profissional_solicitante']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados do Profissional Solicitante / Prestador</td></tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>15 - Conselho</b><br>{d['conselho_profissional']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>16 - Nº Conselho</b><br>{d['numero_conselho']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>17 - UF</b><br>{d['uf']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>18 - Código CBO</b><br>{d['codigo_cbo']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>19 - Assinatura</b><br>{d['assinatura_profissional']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados do Atendimento / Procedimentos e Eventos Solicitados</td></tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>20 - Data Atend.</b><br>{d['data_atendimento']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>21 - Ind. Acidente</b><br>{d['indicacao_acidente']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>22 - Tabela</b><br>{d['tabela']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>23 - Cód. Procedimento</b><br>{d['codigo_procedimento']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>24 - Descrição</b><br>{d['descricao_procedimento']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados do Contratado Executante</td></tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>25 - Código Operadora</b><br>{d['codigo_operadora']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>26 - Nome Contratado</b><br>{d['nome_contratado']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>27 - Código CNES</b><br>{d['cnes']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados do Atendimento / Execução</td></tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>28 - Tipo</b><br>{d['tipo_atendimento']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>29 - Motivo Enc.</b><br>{d['motivo_encaminhamento']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>30 - Regime</b><br>{d['regime_atendimento']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>31 - Saúde Ocup.</b><br>{d['saude_ocupacional']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Dados dos Procedimentos Executados</td></tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>32 - Data Inic.</b><br>{d['data_inicial']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>33 - Data Final</b><br>{d['data_final']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>34 - Cód.</b><br>{d['codigo_procedimento']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>35 - Descrição</b><br>{d['descricao_procedimento']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>36 - Qtd. Solic.</b><br>{d['qtd_solicitada']}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #000; padding: 3px;"><b>37 - Qtd. Autor.</b><br>{d['qtd_autorizada']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>38 - Qtd. Real.</b><br>{d['qtd_realizada']}</td>
                <td style="border: 1px solid #000; padding: 3px;"><b>39 - Valor Unit.</b><br>{d['valor_unitario']}</td>
                <td colspan="2" style="border: 1px solid #000; padding: 3px;"><b>40 - Valor Total</b><br>{d['valor_total']}</td>
            </tr>
            <tr><td colspan="5" style="background: #f0f0f0; border: 1px solid #000; padding: 3px; font-weight: bold;">Observação / Assinaturas</td></tr>
            <tr>
                <td colspan="5" style="border: 1px solid #000; padding: 3px;"><b>41 - Observação</b><br>{d['observacao']}</td>
            </tr>
            <tr>
                <td colspan="2" style="border: 1px solid #000; padding: 10px; text-align: center;"><b>Assinatura do Profissional</b><br>________________________</td>
                <td colspan="1" style="border: 1px solid #000; padding: 10px; text-align: center;"><b>42-60</b><br>(Demais campos)</td>
                <td colspan="2" style="border: 1px solid #000; padding: 10px; text-align: center;"><b>Assinatura do Contratado</b><br>________________________</td>
            </tr>
        </table>
    </div>
    """
    return html

# ============================================
# MENU LATERAL
# ============================================
with st.sidebar:
    st.markdown("### 🧭 Navegação")
    if "pagina" not in st.session_state:
        st.session_state.pagina = "🗓️ Agendamento"

    if st.button("🗓️ Agendamento"):
        st.session_state.pagina = "🗓️ Agendamento"
        st.rerun()
    if st.button("👤 Pacientes"):
        st.session_state.pagina = "👤 Pacientes"
        st.rerun()
    if st.button("👨‍⚕️ Profissionais"):
        st.session_state.pagina = "👨‍⚕️ Profissionais"
        st.rerun()
    if st.button("📋 Gerenciador"):
        st.session_state.pagina = "📋 Gerenciador"
        st.rerun()
    if st.button("✅ Faturar"):
        st.session_state.pagina = "✅ Faturar"
        st.rerun()
    if st.button("📂 Importar"):
        st.session_state.pagina = "📂 Importar"
        st.rerun()
    if st.button("⚙️ Valores"):
        st.session_state.pagina = "⚙️ Valores"
        st.rerun()
    if st.button("🖨️ Guia"):
        st.session_state.pagina = "🖨️ Guia"
        st.rerun()
    if st.button("💰 Financeiro"):
        st.session_state.pagina = "💰 Financeiro"
        st.rerun()

    st.markdown("---")
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

menu = st.session_state.pagina

# ============================================
# ABA: AGENDAMENTO (COM HORÁRIOS)
# ============================================
if menu == "🗓️ Agendamento":
    st.markdown("## 🗓️ Agendamento de Sessões")
    st.caption("Aqui você planeja as sessões de cada paciente por profissional. O sistema calcula as datas automaticamente.")

    pacientes = carregar_pacientes()
    profissionais = carregar_profissionais()

    if not pacientes:
        st.warning("Cadastre um paciente na aba '👤 Pacientes' antes de agendar.")
    if not profissionais:
        st.warning("Cadastre um profissional na aba '👨‍⚕️ Profissionais' antes de agendar.")

    if pacientes and profissionais:
        with st.form("form_agendamento"):
            st.markdown("#### 🧑‍🤝‍🧑 Dados do Paciente e Profissional")
            col1, col2 = st.columns(2)
            with col1:
                paciente_sel = st.selectbox("Paciente", list(pacientes.keys()))
                profissionais_list = list(profissionais.keys())
                profissional_sel = st.selectbox("Profissional", profissionais_list)
            with col2:
                lista_proc = [f"{cod} - {dados['procedimento']}" for cod, dados in TABELA_VALORES.items()]
                procedimento_sel = st.selectbox("Procedimento", lista_proc)

            st.markdown("#### 📅 Planejamento das Sessões")
            col3, col4, col5 = st.columns(3)
            with col3:
                num_sessoes = st.number_input("Número de Sessões Liberadas", min_value=1, step=1, value=10)
            with col4:
                dias_semana = st.multiselect("Dias da Semana", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"])
            with col5:
                data_inicio = st.date_input("Data de Início")

            # **NOVO: Campo de Horário**
            col6, col7 = st.columns(2)
            with col6:
                horario_sessao = st.time_input("Horário da Sessão", value=datetime.strptime("08:00", "%H:%M").time())
            with col7:
                st.write("")  # Espaço vazio para alinhamento

            submitted = st.form_submit_button("🚀 Gerar Agendamentos")

        if submitted:
            if not dias_semana:
                st.error("Selecione pelo menos um dia da semana.")
            else:
                mapa_dias = {"Segunda": 0, "Terça": 1, "Quarta": 2, "Quinta": 3, "Sexta": 4}
                dias_numeros = [mapa_dias[d] for d in dias_semana]

                codigo_proc = procedimento_sel.split(" - ")[0]
                valor = TABELA_VALORES[codigo_proc]['valor']
                horario_str = horario_sessao.strftime("%H:%M")

                datas_geradas = []
                data_atual = data_inicio
                while len(datas_geradas) < num_sessoes:
                    if data_atual.weekday() in dias_numeros:
                        datas_geradas.append(data_atual)
                    data_atual += timedelta(days=1)

                for data in datas_geradas:
                    nova_linha = pd.DataFrame([{
                        'Paciente': paciente_sel,
                        'Guia': f'GUIA_{codigo_proc}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'Profissional': profissional_sel,
                        'Data_Sessao': data.strftime('%Y-%m-%d'),
                        'Horario_Sessao': horario_str,
                        'Status_Sessao': 'Agendada',
                        'Status_Faturamento': 'Pendente',
                        'Valor': valor
                    }])
                    df = pd.concat([df, nova_linha], ignore_index=True)

                salvar_dados()
                st.success(f"✅ {len(datas_geradas)} sessões geradas para {paciente_sel} com {profissional_sel} às {horario_str}!")
                st.balloons()
                st.rerun()

# ============================================
# ABA: CADASTRO DE PACIENTES
# ============================================
elif menu == "👤 Pacientes":
    st.markdown("## 👤 Cadastro de Pacientes")

    with st.form("form_paciente"):
        nome = st.text_input("Nome do Paciente *")
        guia = st.text_input("Número da Guia (opcional)")

        col1, col2 = st.columns(2)
        with col1:
            num_sessoes = st.number_input("Sessões Liberadas (Geral)", min_value=1, step=1, value=10)
        with col2:
            procedimento = st.selectbox("Procedimento Principal", list(TABELA_VALORES.keys()), format_func=lambda x: f"{x} - {TABELA_VALORES[x]['procedimento']}")

        submitted = st.form_submit_button("💾 Salvar Cadastro")

    if submitted:
        if not nome:
            st.error("O nome do paciente é obrigatório.")
        else:
            pacientes = carregar_pacientes()
            pacientes[nome] = {
                "guia": guia,
                "num_sessoes": num_sessoes,
                "procedimento": procedimento,
                "dias": []
            }
            salvar_pacientes(pacientes)
            st.success(f"Paciente {nome} cadastrado com sucesso!")
            st.rerun()

    st.markdown("### 📋 Pacientes Cadastrados")
    pacientes = carregar_pacientes()
    if pacientes:
        for nome, dados in pacientes.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{nome}** - Guia: {dados['guia']} | Sessões: {dados['num_sessoes']} | Procedimento: {TABELA_VALORES[dados['procedimento']]['procedimento']}")
            with col2:
                if st.button("Excluir", key=f"excluir_{nome}"):
                    del pacientes[nome]
                    salvar_pacientes(pacientes)
                    st.rerun()
    else:
        st.info("Nenhum paciente cadastrado ainda.")

# ============================================
# ABA: CADASTRO DE PROFISSIONAIS
# ============================================
elif menu == "👨‍⚕️ Profissionais":
    st.markdown("## 👨‍⚕️ Cadastro de Profissionais")

    with st.form("form_profissional"):
        prof_nome = st.text_input("Nome do Profissional *")
        prof_conselho = st.text_input("Conselho (ex: CRP)")
        prof_num = st.text_input("Número do Conselho")

        submitted = st.form_submit_button("💾 Salvar Cadastro")

    if submitted:
        if not prof_nome:
            st.error("O nome do profissional é obrigatório.")
        else:
            profissionais = carregar_profissionais()
            profissionais[prof_nome] = {
                "conselho": prof_conselho,
                "numero": prof_num
            }
            salvar_profissionais(profissionais)
            st.success(f"Profissional {prof_nome} cadastrado com sucesso!")
            st.rerun()

    st.markdown("### 📋 Profissionais Cadastrados")
    profissionais = carregar_profissionais()
    if profissionais:
        for nome, dados in profissionais.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{nome}** - {dados['conselho']} {dados['numero']}")
            with col2:
                if st.button("Excluir", key=f"excluir_prof_{nome}"):
                    del profissionais[nome]
                    salvar_profissionais(profissionais)
                    st.rerun()
    else:
        st.info("Nenhum profissional cadastrado ainda.")

# ============================================
# ABA: GERENCIADOR (COM EXIBIÇÃO DE HORÁRIO)
# ============================================
elif menu == "📋 Gerenciador":
    st.markdown("## 📋 Gerenciador de Sessões")
    if len(df) > 0:
        df = df.sort_values(by='Data_Sessao', ascending=False)
        busca = st.text_input("🔍 Buscar por paciente, guia ou profissional")

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

        df_filtrado = df.copy()
        if filtro_paciente != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Paciente'] == filtro_paciente]
        if filtro_status != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status_Sessao'] == filtro_status]
        if busca:
            df_filtrado = df_filtrado[
                df_filtrado['Paciente'].str.contains(busca, case=False, na=False) |
                df_filtrado['Guia'].str.contains(busca, case=False, na=False) |
                df_filtrado['Profissional'].str.contains(busca, case=False, na=False)
            ]

        df_filtrado = formatar_datas(df_filtrado)
        if 'Valor' in df_filtrado.columns:
            df_filtrado['Valor'] = df_filtrado['Valor'].apply(formatar_moeda)

        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✅ Marcar Sessão como Realizada")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            paciente_sel = st.selectbox("Selecione o Paciente", df['Paciente'].unique(), key="paciente_sel")
        with col2:
            datas = df[df['Paciente'] == paciente_sel]['Data_Sessao'].unique()
            data_sel = st.selectbox("Selecione a Data", datas, key="data_sel") if len(datas) > 0 else None
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
        st.info("📭 Nenhuma sessão cadastrada. Vá para a aba **📂 Importar**.")

# ============================================
# ABA: FATURAR
# ============================================
elif menu == "✅ Faturar":
    st.markdown("## ✅ Gerenciamento de Faturamento")
    if len(df) > 0:
        prontas = df[df['Status_Faturamento'] == 'Pronto']
        st.markdown(f"### 📋 Sessões Prontas para Faturar: {len(prontas)}")
        if len(prontas) > 0:
            prontas_view = formatar_datas(prontas.copy())
            if 'Valor' in prontas_view.columns:
                prontas_view['Valor'] = prontas_view['Valor'].apply(formatar_moeda)
            st.dataframe(prontas_view, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### 📝 Formulário de Faturamento")

            pacientes_dict = carregar_pacientes()
            profissionais_dict = carregar_profissionais()
            lista_pacientes = list(pacientes_dict.keys())
            lista_profissionais = list(profissionais_dict.keys())

            pacientes_prontos = prontas['Paciente'].unique()
            paciente_faturamento = st.selectbox("Selecione o Paciente para Faturar", pacientes_prontos)

            if paciente_faturamento in pacientes_dict:
                dados_pac = pacientes_dict[paciente_faturamento]
                st.info(f"**Paciente:** {paciente_faturamento} | **Guia:** {dados_pac.get('guia', 'N/A')}")

            datas_prontas = prontas[prontas['Paciente'] == paciente_faturamento]['Data_Sessao'].unique()
            data_faturamento = st.selectbox("Selecione a Data da Sessão", datas_prontas)

            st.markdown("#### 👨‍⚕️ Dados do Profissional")
            if lista_profissionais:
                prof_faturamento = st.selectbox("Selecione o Profissional", lista_profissionais)
                dados_prof = profissionais_dict[prof_faturamento]
            else:
                prof_faturamento = st.text_input("Nome do Profissional")
                dados_prof = {"conselho": "", "numero": ""}

            st.markdown("#### 📁 Dados da Guia")
            col1, col2 = st.columns(2)
            with col1:
                guia_prestador = st.text_input("Guia do Prestador")
                guia_principal = st.text_input("Guia Principal")
                guia_operadora = st.text_input("Guia da Operadora")
                senha_guia = st.text_input("Senha")
                data_operacao = st.date_input("Data da Operação")
            with col2:
                num_carteirinha = st.text_input("Número da Carteirinha")
                st.text_input("Código da Operadora/CNPJ", value="42.725.338/0001-50", disabled=True)
                st.text_input("Nome do Contratado", value="TEA Espaço Terapêutico", disabled=True)
                st.text_input("CNES", value="4.199.650", disabled=True)

            st.markdown("#### 🏥 Dados do Atendimento")
            col5, col6 = st.columns(2)
            with col5:
                carater_atendimento = st.selectbox("Caráter de Atendimento", ["Eletiva", "Urgência"])
                tipo_atendimento = st.text_input("Tipo de Atendimento", value="Terapias")
                indicacao_acidente = st.selectbox("Indicação de Acidente", ["Não acidente", "Acidente"])

            st.markdown("---")
            if st.button("✅ Confirmar Faturamento", use_container_width=True, type="primary"):
                mask = (df['Paciente'] == paciente_faturamento) & (df['Data_Sessao'] == data_faturamento)
                if mask.any():
                    idx = df[mask].index[0]
                    df.loc[idx, 'Guia_Prestador'] = guia_prestador
                    df.loc[idx, 'Guia_Principal'] = guia_principal
                    df.loc[idx, 'Guia_Operadora'] = guia_operadora
                    df.loc[idx, 'Senha'] = senha_guia
                    df.loc[idx, 'Data_Operacao'] = data_operacao.strftime('%Y-%m-%d')
                    df.loc[idx, 'Num_Carteirinha'] = num_carteirinha
                    df.loc[idx, 'Codigo_Operadora'] = "42.725.338/0001-50"
                    df.loc[idx, 'Nome_Contratado'] = "TEA Espaço Terapêutico"
                    df.loc[idx, 'CNES'] = "4.199.650"
                    df.loc[idx, 'Nome_Profissional'] = prof_faturamento
                    df.loc[idx, 'Conselho_Profissional'] = dados_prof.get('conselho', '')
                    df.loc[idx, 'Num_Conselho'] = dados_prof.get('numero', '')
                    df.loc[idx, 'Carater_Atendimento'] = carater_atendimento
                    df.loc[idx, 'Tipo_Atendimento'] = tipo_atendimento
                    df.loc[idx, 'Indicacao_Acidente'] = indicacao_acidente

                    df.loc[idx, 'Status_Sessao'] = 'Faturada'
                    df.loc[idx, 'Status_Faturamento'] = 'Faturado'
                    salvar_dados()
                    st.success(f"✅ Guia de {paciente_faturamento} faturada com sucesso!")
                    st.balloons()
                    st.rerun()
        else:
            st.info("✅ Nenhuma sessão pronta para faturar.")
    else:
        st.info("📭 Nenhuma sessão cadastrada.")

# ============================================
# ABA: IMPORTAR
# ============================================
elif menu == "📂 Importar":
    st.markdown("## 📂 Importar Guias")
    uploaded_files = st.file_uploader("📎 Selecione os PDFs das guias", type=['pdf'], accept_multiple_files=True)

    pacientes = carregar_pacientes()
    lista_pacientes = list(pacientes.keys())
    paciente_import = st.selectbox("Selecione o Paciente", ["Novo Paciente (usar nome do arquivo)"] + lista_pacientes)

    profissionais = carregar_profissionais()
    lista_profissionais = list(profissionais.keys())
    if lista_profissionais:
        profissional_import = st.selectbox("Selecione o Profissional", lista_profissionais)
    else:
        profissional_import = "Psicólogo"

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")
        st.markdown("#### 🧾 Selecione o Procedimento Realizado")
        lista_procedimentos = [f"{cod} - {dados['procedimento']} (R$ {dados['valor']:.2f})" for cod, dados in TABELA_VALORES.items()]
        procedimento_sel = st.selectbox("Procedimento", lista_procedimentos)
        codigo_sel = procedimento_sel.split(" - ")[0]
        valor_correto = TABELA_VALORES[codigo_sel]['valor']
        st.info(f"Valor a ser aplicado: **{formatar_moeda(valor_correto)}**")

        if st.button("🚀 Importar Guias", use_container_width=True):
            with st.spinner("Processando..."):
                for file in uploaded_files:
                    temp_path = BASE_DIR / "1_Inputs" / file.name
                    with open(temp_path, "wb") as f:
                        f.write(file.getbuffer())

                    if paciente_import != "Novo Paciente (usar nome do arquivo)":
                        nome_paciente = paciente_import
                    else:
                        nome_paciente = file.name.replace(".pdf", "").replace("_", " ").title()

                    nova_linha = pd.DataFrame([{
                        'Paciente': nome_paciente,
                        'Guia': f'GUIA{datetime.now().strftime("%Y%m%d%H%M%S")}',
                        'Profissional': profissional_import,
                        'Data_Sessao': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                        'Horario_Sessao': "",
                        'Status_Sessao': 'Agendada',
                        'Status_Faturamento': 'Pendente',
                        'Valor': valor_correto
                    }])
                    df = pd.concat([df, nova_linha], ignore_index=True)

                df.to_excel(caminho_excel, index=False)
                st.success(f"🎉 {len(uploaded_files)} guia(s) importada(s) com sucesso! Valor aplicado: {formatar_moeda(valor_correto)}")
                st.balloons()
                st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Sessões Cadastradas")
    if len(df) > 0:
        df_view = df.sort_values(by='Data_Sessao', ascending=False)
        busca = st.text_input("🔍 Buscar sessão cadastrada")
        if busca:
            df_view = df_view[
                df_view['Paciente'].str.contains(busca, case=False, na=False) |
                df_view['Guia'].str.contains(busca, case=False, na=False)
            ]

        df_view = formatar_datas(df_view)
        if 'Valor' in df_view.columns:
            df_view['Valor'] = df_view['Valor'].apply(formatar_moeda)

        st.dataframe(df_view, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma sessão cadastrada ainda.")

# ============================================
# ABA: VALORES
# ============================================
elif menu == "⚙️ Valores":
    st.markdown("## ⚙️ Atualização de Valores")
    st.caption("Atualize os valores dos procedimentos conforme necessário. As alterações são salvas automaticamente.")

    df_valores = pd.DataFrame([
        {"Código": cod, "Procedimento": dados["procedimento"], "Valor (R$)": f"R$ {dados['valor']:.2f}"}
        for cod, dados in TABELA_VALORES.items()
    ])

    df_editado = st.data_editor(
        df_valores,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Código": st.column_config.TextColumn("Código", disabled=True),
            "Procedimento": st.column_config.TextColumn("Procedimento", disabled=True),
            "Valor (R$)": st.column_config.TextColumn("Valor (R$)", disabled=True)
        }
    )

    if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
        nova_tabela = {}
        for _, row in df_editado.iterrows():
            valor_limpo = row["Valor (R$)"].replace("R$", "").replace(" ", "").replace(",", ".")
            nova_tabela[str(row["Código"])] = {
                "procedimento": row["Procedimento"],
                "valor": float(valor_limpo)
            }

        salvar_valores(nova_tabela)
        TABELA_VALORES = nova_tabela
        st.success("✅ Valores atualizados com sucesso!")
        st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Valores Atuais")
    st.dataframe(df_valores, use_container_width=True, hide_index=True)

# ============================================
# ABA: GUIA (MODO PAISAGEM)
# ============================================
elif menu == "🖨️ Guia":
    st.markdown("## 🖨️ Visualização de Guia (Padrão CASSI)")
    st.caption("Guia completa com todos os campos, em modo paisagem.")

    if len(df) > 0:
        pacientes_unicos = df['Paciente'].unique()
        paciente_sel = st.selectbox("Selecione o Paciente", pacientes_unicos)

        datas_sessao = df[df['Paciente'] == paciente_sel]['Data_Sessao'].unique()
        if len(datas_sessao) > 0:
            data_sel = st.selectbox("Selecione a Data da Sessão", datas_sessao)

            mask = (df['Paciente'] == paciente_sel) & (df['Data_Sessao'] == data_sel)
            sessao = df[mask].iloc[0]

            pacientes_dict = carregar_pacientes()
            profissionais_dict = carregar_profissionais()

            dados_paciente = pacientes_dict.get(paciente_sel, {})
            profissional_nome = sessao.get('Profissional', 'Não definido')
            dados_prof = profissionais_dict.get(profissional_nome, {})

            valor_sessao = sessao.get('Valor', 0)
            try:
                valor_sessao = float(valor_sessao)
            except:
                valor_sessao = 0
            valor_formatado = formatar_moeda(valor_sessao)

            dados_guia = {
                'guia_prestador': dados_paciente.get('guia', sessao.get('Guia', '346659')),
                'guia_principal': dados_paciente.get('guia_principal', '796105836'),
                'guia_operadora': dados_paciente.get('guia_operadora', '796105837'),
                'data_autorizacao': datetime.now().strftime('%d/%m/%Y'),
                'senha': dados_paciente.get('senha', '323397688'),
                'validade_senha': datetime.now().strftime('%d/%m/%Y'),
                'carteirinha': dados_paciente.get('carteirinha', '001004457890358'),
                'nome_beneficiario': paciente_sel.upper(),
                'validade_carteira': datetime.now().strftime('%d/%m/%Y'),
                'atendimento_rn': "N",
                'codigo_operadora': "94509024",
                'nome_contratado': "TEA ESPACO TERAPEUTICO LTDA",
                'nome_profissional_solicitante': profissional_nome.upper() if profissional_nome else "NÃO INFORMADO",
                'conselho_profissional': dados_prof.get('conselho', 'CRP'),
                'numero_conselho': dados_prof.get('numero', '823349'),
                'uf': "PR",
                'codigo_cbo': "251510",
                'assinatura_profissional': "________________________",
                'data_atendimento': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'indicacao_acidente': "9 - NÃO ACIDENTE",
                'tabela': "22",
                'codigo_procedimento': "50000470",
                'descricao_procedimento': "SESSÃO DE PSICOTERAPIA INDIVIDUAL POR PSICÓLOGO",
                'tipo_atendimento': "Terapias",
                'motivo_encaminhamento': "01",
                'regime_atendimento': "01",
                'saude_ocupacional': "N",
                'data_inicial': datetime.now().strftime('%d/%m/%Y'),
                'data_final': datetime.now().strftime('%d/%m/%Y'),
                'qtd_solicitada': "1",
                'qtd_autorizada': "1",
                'qtd_realizada': "1",
                'valor_unitario': valor_formatado,
                'valor_total': valor_formatado,
                'observacao': "",
                'cnes': "4.199.650"
            }

            guia_html = render_guia_cassi(dados_guia)
            components.html(guia_html, height=1400, scrolling=True)

            st.markdown("---")
            if st.button("🖨️ Imprimir Guia"):
                st.success("Para imprimir, pressione Ctrl+P no seu teclado e selecione 'Salvar como PDF' ou a impressora desejada.")
        else:
            st.info("Nenhuma sessão encontrada para este paciente.")
    else:
        st.info("Nenhuma sessão cadastrada ainda. Importe ou agende uma sessão para visualizar a guia.")

# ============================================
# ABA: FINANCEIRO
# ============================================
elif menu == "💰 Financeiro":
    st.markdown("## 💰 Painel Financeiro")
    st.caption("Acompanhe os valores faturados, agendados e pendentes.")

    if len(df) > 0:
        df_fin = df.copy()
        df_fin['Valor'] = pd.to_numeric(df_fin['Valor'], errors='coerce').fillna(0)

        col1, col2 = st.columns(2)
        with col1:
            meses = df_fin['Data_Sessao'].astype(str).str[:7].unique()
            meses = sorted(meses, reverse=True)
            filtro_mes = st.selectbox("Filtrar por Mês (AAAA-MM)", ["Todos"] + list(meses))
        with col2:
            profissionais = ['Todos'] + list(df_fin['Profissional'].unique())
            filtro_profissional = st.selectbox("Filtrar por Profissional", profissionais)

        if filtro_mes != "Todos":
            df_fin = df_fin[df_fin['Data_Sessao'].astype(str).str[:7] == filtro_mes]
        if filtro_profissional != "Todos":
            df_fin = df_fin[df_fin['Profissional'] == filtro_profissional]

        total_agendado = df_fin[df_fin['Status_Sessao'] == 'Agendada']['Valor'].sum()
        total_realizado = df_fin[df_fin['Status_Sessao'] == 'Realizada']['Valor'].sum()
        total_pronto = df_fin[df_fin['Status_Faturamento'] == 'Pronto']['Valor'].sum()
        total_faturado = df_fin[df_fin['Status_Faturamento'] == 'Faturado']['Valor'].sum()
        total_geral = df_fin['Valor'].sum()

        st.markdown("### 📊 Resumo Financeiro")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Agendado", formatar_moeda(total_agendado))
        with col2:
            st.metric("Realizado", formatar_moeda(total_realizado))
        with col3:
            st.metric("Pronto p/ Faturar", formatar_moeda(total_pronto))
        with col4:
            st.metric("Faturado", formatar_moeda(total_faturado))
        with col5:
            st.metric("Total Geral", formatar_moeda(total_geral))

        st.markdown("---")
        st.markdown("### 📥 Exportar Dados")
        if st.button("📥 Baixar Relatório (Excel)"):
            export_data = df_fin.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=export_data,
                file_name=f"relatorio_financeiro_{filtro_mes}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhuma sessão cadastrada ainda.")