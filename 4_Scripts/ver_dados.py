import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
caminho = BASE_DIR / "2_outputs" / "controle_avancado.xlsx"

if caminho.exists():
    df = pd.read_excel(caminho)
    print("=" * 60)
    print("📊 DADOS ATUAIS")
    print("=" * 60)
    print(df)
    print("=" * 60)
    print(f"Total de sessões: {len(df)}")
    prontas = len(df[df['Status_Faturamento'] == 'Pronto'])
    print(f"Prontas para faturar: {prontas}")
else:
    print("⚠️ Nenhum dado encontrado. Criando dados de exemplo...")
    
    dados = [
        ['ICARO GLUCK', '796105837', 'Psicólogo', '2026-09-02', 'Realizada', 'Pronto', 150.00],
        ['ICARO GLUCK', '796105837', 'Psicólogo', '2026-09-04', 'Realizada', 'Pronto', 150.00],
        ['ICARO GLUCK', '796105837', 'Psicólogo', '2026-09-06', 'Realizada', 'Pronto', 150.00],
        ['ICARO GLUCK', '796105837', 'Psicólogo', '2026-09-08', 'Agendada', 'Pendente', 150.00],
    ]
    df = pd.DataFrame(dados, columns=['Paciente', 'Guia', 'Profissional', 'Data_Sessao', 'Status_Sessao', 'Status_Faturamento', 'Valor'])
    df.to_excel(caminho, index=False)
    print("✅ Dados criados com sucesso!")
    print(df)