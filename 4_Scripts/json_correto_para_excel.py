import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def converter_json_correto():
    print("=" * 60)
    print("📊 CONVERSOR JSON (COM DADOS) → EXCEL")
    print("=" * 60)
    
    # Usa o JSON que tem dados
    caminho_json = BASE_DIR / "2_outputs" / "guia modelo (1)_dados.json"
    
    if not caminho_json.exists():
        print("❌ Arquivo com dados não encontrado!")
        return
    
    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    
    # Cria uma linha com todos os campos
    linha = {'Arquivo': 'guia modelo (1).pdf'}
    
    # Adiciona todos os campos
    for chave, valor in dados.items():
        if valor != "Nao_encontrado" and valor:
            linha[chave] = valor
    
    # Cria DataFrame
    df = pd.DataFrame([linha])
    
    # Salva como Excel
    caminho_excel = BASE_DIR / "2_outputs" / "dados_corretos.xlsx"
    df.to_excel(caminho_excel, index=False)
    
    print(f"\n✅ Planilha salva em: {caminho_excel}")
    print(f"\n📊 Campos preenchidos: {len(linha) - 1}")
    print("\n🎉 Conversão concluída!")

if __name__ == "__main__":
    converter_json_correto()