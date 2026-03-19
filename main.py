import pandas as pd
import json
import requests
from analyzer import MarketAnalyzer

TOKEN = "8295418707:AAEJ38tqvt31EagPQkEuMG1CImFI-LCrrXg"
CHAT_ID = "8798226748"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except:
        pass

def main():
    print("\n🌍 --- AI MARKET SENTINEL v6: MOTOR UNIVERSAL ---")
    
    try:
        with open("market_data_history.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar banco de dados: {e}")
        return

    termo = input("🔍 O que você quer analisar hoje? ").strip()

    analyzer = MarketAnalyzer(dados)
    
    # IMPORTANTE: Receber o retorno das funções nas variáveis
    df_filtrado = analyzer.filtrar_por_nome(termo)
    df_final = analyzer.classificar_ofertas()

    if df_final is None or df_final.empty:
        print(f"⚠️ Nenhum resultado consistente para '{termo}'.")
        return

    # Limpeza e Ordenação
    df_exibir = df_final.drop_duplicates(subset=['nome', 'preco']).sort_values(by='preco')

    # Telegram
    reliquias = df_exibir[df_exibir['tier'] == 'S - Relíquia']
    if not reliquias.empty:
        enviar_telegram(f"🎯 *OPORTUNIDADE:* {termo.upper()}")
        for _, row in reliquias.head(2).iterrows():
            enviar_telegram(f"💎 *RANK S:* {row['nome']}\n💰 R$ {row['preco']:.2f}")

    print(f"\n📊 ANÁLISE DE MERCADO: {termo}")
    print(df_exibir[['nome', 'preco', 'tier']].head(15).to_string(index=False))

    df_exibir.to_json("market_data_analisado.json", orient="records", indent=4, force_ascii=False)
    print("\n✅ Power BI atualizado!")

if __name__ == "__main__":
    main()