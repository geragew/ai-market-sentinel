import os
import pandas as pd
import json
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DE SEGURANÇA ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class AIMarketAnalyzer:
    def __init__(self, dados):
        self.df = pd.DataFrame(dados)
        self.df_filtrado = pd.DataFrame()

    def filtrar_por_nome(self, termo):
        if self.df.empty: return pd.DataFrame()
        palavras = termo.lower().split()
        self.df_filtrado = self.df[
            self.df['produto'].str.lower().apply(lambda x: all(p in x for p in palavras))
        ].copy()
        return self.df_filtrado

    def classificar_ofertas(self):
        if self.df_filtrado.empty: return pd.DataFrame()
        
        self.df_filtrado['preco'] = pd.to_numeric(self.df_filtrado['preco'], errors='coerce')
        topo = self.df_filtrado['preco'].max()
        if topo > 500:
            self.df_filtrado = self.df_filtrado[self.df_filtrado['preco'] >= (topo * 0.4)]

        media = self.df_filtrado['preco'].mean()
        
        def definir_tier(preco):
            if preco < media * 0.85: return '💎 S - RELÍQUIA'
            if preco < media: return '✅ A - PREÇO JUSTO'
            return '⚠️ B - ACIMA DA MÉDIA'

        self.df_filtrado['tier'] = self.df_filtrado['preco'].apply(definir_tier)
        return self.df_filtrado

def enviar_telegram(mensagem):
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown"
        try:
            requests.get(url, timeout=5)
        except:
            pass

def main():
    # Limpa o terminal antes de começar
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("="*65)
    print("        🌍 SENTINEL v6 - INTELIGÊNCIA DE MERCADO")
    print("="*65)
    
    file_path = "market_data_history.json"
    
    # --- CORREÇÃO DO ERRO DE SINTAXE AQUI ---
    if not os.path.exists(file_path):
        print("\n❌ ERRO: Banco de dados 'market_data_history.json' não encontrado.")
        print("💡 Rode o coletor primeiro para gerar os dados!")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"\n❌ ERRO AO LER JSON: {e}")
        return

    termo = input("\n🔍 O QUE DESEJA ANALISAR HOJE? ").strip()
    if not termo: return

    print(f"\n⚙️  Analisando histórico para: {termo.upper()}...")
    
    analyzer = AIMarketAnalyzer(dados)
    analyzer.filtrar_por_nome(termo)
    df_final = analyzer.classificar_ofertas()

    if df_final is None or df_final.empty:
        print(f"\n[!] Nada relevante no histórico para '{termo}'.")
        return

    df_exibir = df_final.sort_values(by='preco')
    
    print("\n" + "-"*65)
    print(f"{'PRODUTO':<38} | {'PREÇO':<10} | {'STATUS'}")
    print("-"*65)

    for _, row in df_exibir.head(10).iterrows():
        nome_limpo = (row['produto'][:35] + '..') if len(row['produto']) > 35 else row['produto']
        print(f"{nome_limpo:<38} | R${row['preco']:>8.2f} | {row['tier']}")

    # Alertas para o Telegram
    reliquias = df_exibir[df_exibir['tier'] == '💎 S - RELÍQUIA']
    if not reliquias.empty:
        print("\n🔥 SUCESSO: Oportunidades detectadas!")
        for _, row in reliquias.head(2).iterrows():
            msg = (f"🚨 *OFERTA RELÍQUIA!*\n\n"
                   f"📦 {row['produto']}\n"
                   f"💰 *Preço:* R$ {row['preco']:.2f}\n"
                   f"🛒 [LINK AMAZON]({row.get('link', '')})")
            enviar_telegram(msg)

    # Export final
    df_exibir.to_json("market_data_analisado.json", orient="records", indent=4, force_ascii=False)
    
    print("\n" + "="*65)
    print("✅ ANÁLISE CONCLUÍDA | DADOS PRONTOS PARA POWER BI")
    print("="*65)

if __name__ == "__main__":
    main()