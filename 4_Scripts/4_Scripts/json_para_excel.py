import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def json_para_excel():
    print("=" * 60)
    print("📊 CONVERSOR JSON → EXCEL")
    print("=" * 60)
    
    # Abre o relatório JSON
    caminho_json = BASE_DIR / "2_outputs" / "relatorio_completo.json"
    
    if not caminho_json.exists():
        print("❌ Arquivo relatorio_completo.json não encontrado!")
        print("   Execute primeiro o processador_lote.py")
        return
    
    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Lista para armazenar todas as linhas
    linhas = []
    
    # Nomes dos campos (mapeamento número → nome)
    nomes_campos = {
        "1": "Registro_ANS",
        "2": "Numero_Guia_Prestador",
        "3": "Numero_Guia_Principal",
        "4": "Data_Autorizacao",
        "5": "Senha",
        "6": "Data_Validade_Senha",
        "7": "Numero_Guia",
        "8": "Numero_Carteira",
        "9": "Validade_Carteira",
        "10": "Nome_Beneficiario",
        "11": "Codigo_Plano",
        "12": "Atendimento_RN",
        "13": "Codigo_Operadora",
        "14": "Nome_Contratado",
        "15": "Nome_Profissional_Solicitante",
        "16": "Conselho_Profissional",
        "17": "Numero_Conselho",
        "18": "UF",
        "19": "Codigo_CBO",
        "20": "Assinatura_Profissional_Solicitante",
        "21": "Carater_Atendimento",
        "22": "Data_Solicitacao",
        "23": "Indicacao_Clinica",
        "24": "Tabela",
        "25": "Codigo_Procedimento",
        "26": "Descricao_Procedimento",
        "27": "Qt_Solicitada",
        "28": "Qt_Autorizada",
        "29": "Codigo_Operadora_Executante",
        "30": "Nome_Contratado_Executante",
        "31": "Codigo_CNES",
        "32": "Tipo_Atendimento",
        "33": "Indicador_Acidente",
        "34": "Tipo_Consulta",
        "35": "Motivo_Encerramento",
        "36": "Data_Execucao",
        "37": "Hora_Inicial",
        "38": "Hora_Final",
        "39": "Tabela_Execucao",
        "40": "Codigo_Procedimento_Executado",
        "41": "Descricao_Procedimento_Executado",
        "42": "Quantidade",
        "43": "Via",
        "44": "Tecnica",
        "45": "Fator_Reducao_Acrescimo",
        "46": "Valor_Total",
        "47": "Assinatura_Responsavel",
        "48": "Seq_Ref",
        "49": "Grau_Participacao",
        "50": "Codigo_Operadora_CPF",
        "51": "Nome_Profissional_Executante",
        "52": "Conselho_Profissional_Executante",
        "53": "Numero_Conselho_Executante",
        "54": "UF_Executante",
        "55": "Codigo_CBO_Executante",
        "56": "Data_Realizacao_Procedimentos_Serie",
        "57": "Assinatura_Beneficiario",
        "58": "Observacao_Justificativa",
        "59": "Total_Procedimentos",
        "60": "Total_Taxas_Alugueis",
        "61": "Total_Materiais",
        "62": "Total_OPME",
        "63": "Total_Medicamentos",
        "64": "Total_Gases_Medicinais",
        "65": "Total_Geral",
        "66": "Assinatura_Responsavel_Autorizacao",
        "67": "Assinatura_Contratado"
    }
    
    # Para cada arquivo PDF processado
    for nome_arquivo, campos in dados['arquivos'].items():
        # Cria uma linha com todos os campos
        linha = {'Arquivo': nome_arquivo}
        
        # Preenche cada campo
        for num, nome in nomes_campos.items():
            valor = campos.get(num, '')
            linha[nome] = valor
        
        linhas.append(linha)
    
    # Cria DataFrame
    df = pd.DataFrame(linhas)
    
    # Salva como Excel
    caminho_excel = BASE_DIR / "2_outputs" / "dados_completos.xlsx"
    df.to_excel(caminho_excel, index=False)
    
    print(f"\n✅ Planilha salva em: {caminho_excel}")
    
    # Mostra resumo
    print(f"\n📊 Resumo:")
    print(f"   Total de guias processadas: {len(linhas)}")
    print(f"   Total de campos por guia: {len(nomes_campos)}")
    
    # Mostra quantos campos foram preenchidos em média
    total_campos = 0
    for linha in linhas:
        preenchidos = sum(1 for k, v in linha.items() if k != 'Arquivo' and v)
        total_campos += preenchidos
    
    if linhas:
        media = total_campos / len(linhas)
        print(f"   Média de campos preenchidos por guia: {media:.1f}")
    
    print("\n🎉 Conversão concluída!")

if __name__ == "__main__":
    json_para_excel()