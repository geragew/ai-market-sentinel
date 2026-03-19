import os
import pandas as pd
import json
from datetime import datetime

# --- CONFIGURAÇÃO DE SEGURANÇA ---
TOKEN = os.getenv("TELEGRAM_TOKEN") 
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

class AIMarketAnalyzer:
    def __init__(self, dados):
        self.df = pd.DataFrame(dados)
        self.df_filtrado = pd.DataFrame()

    def filtrar_por_nome(self, termo):
        # Transforma a busca em palavras-chave para ser universal
        palavras = termo.lower().split()
        self.df_filtrado = self.df[
            self.df['produto'].str.lower().apply(lambda x: all(p in x for p in palavras))
        ].copy()
        return self.df_filtrado

    def classificar_ofertas(self):
        if self.df_filtrado.empty:
            return pd.DataFrame()
        
        # Converte preço e limpa outliers (o famoso filtro das capinhas)
        self.df_filtrado['preco'] = pd.to_numeric(self.df_filtrado['preco'], errors='coerce')
        topo = self.df_filtrado['preco'].max()
        if topo > 500:
            self.df_filtrado = self.df_filtrado[self.df_filtrado['preco'] >= (topo * 0.4)]

        media = self.df_filtrado['preco'].mean()
        
        # Lógica de Tiers
        def definir_tier(preco):
            if preco < media * 0.85: return 'S - Relíquia'
            if preco < media: return 'A - Justo'
            return 'B - Normal'

        self.df_filtrado['tier'] = self.df_filtrado['preco'].apply(definir_tier)
        return self.df_filtrado

def enviar_telegram(mensagem):
    import requests
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown"
        try:
            requests.get(url)
        except:
            print("⚠️ Falha ao enviar Telegram.")

def main():
    print("\n🌍 --- AI MARKET SENTINEL v6: MOTOR UNIVERSAL ---")
    
    file_path = "market_data_history.json"
    if not os.path.exists(file_path):
        print("❌ Banco de dados não encontrado! Rode o coletor primeiro.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return

    termo = input("🔍 O que você quer analisar hoje? ").strip()
    if not termo: return

    # --- AQUI ESTAVA O ERRO: AJUSTADO PARA AIMarketAnalyzer ---
    analyzer = AIMarketAnalyzer(dados)
    
    analyzer.filtrar_por_nome(termo)
    df_final = analyzer.classificar_ofertas()

    if df_final is None or df_final.empty:
        print(f"⚠️ Nenhum resultado consistente para '{termo}'.")
        return

    # Organização para exibição
    df_exibir = df_final.sort_values(by='preco')

    # Alerta de Relíquias (Telegram)
    reliquias = df_exibir[df_exibir['tier'] == 'S - Relíquia']
    if not reliquias.empty:
        print("💎 Relíquia encontrada! Enviando alerta...")
        for _, row in reliquias.head(2).iterrows():
            msg = f"💎 *RANK S:* {row['produto']}\n💰 R$ {row['preco']:.2f}\n🛒 {row.get('link', 'Sem link')}"
            enviar_telegram(msg)

    print(f"\n📊 ANÁLISE DE MERCADO: {termo}")
    # Ajustado para usar o nome correto da coluna 'produto'
    print(df_exibir[['produto', 'preco', 'tier']].head(10).to_string(index=False))

    # Salva para o Power BI
    df_exibir.to_json("market_data_analisado.json", orient="records", indent=4, force_ascii=False)
    print("\n✅ Banco de dados atualizado para o Power BI!")

if __name__ == "__main__":
    main()