import pandas as pd
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from thefuzz import process # IA para entender palavras erradas

class AIMarketAnalyzer:
    def __init__(self, search_term="notebook gamer"):
        self.base_url = "https://www.amazon.com.br"
        self.search_term = search_term
        self.file_json = "market_data_history.json"
        self.data_raw = []

    def scrape_data(self, max_pages=2):
        print(f"🚀 Iniciando coleta para: {self.search_term}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # --- CAMUFLAGEM PARA NÃO SER BLOQUEADO ---
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            
            page.goto(self.base_url)
            page.fill("#twotabsearchtextbox", self.search_term)
            page.keyboard.press("Enter")
            
            # Espera um pouco mais para a Amazon carregar (evita erro de página vazia)
            page.wait_for_timeout(5000) 

            for p_num in range(1, max_pages + 1):
                print(f"📦 Capturando página {p_num}...")
                try:
                    page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
                    cards = page.query_selector_all("div[data-component-type='s-search-result']")

                    for card in cards:
                        titulo = card.query_selector("h2 span")
                        preco = card.query_selector(".a-price-whole")
                        
                        if titulo and preco:
                            self.data_raw.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "termo_busca": self.search_term,
                                "produto": titulo.inner_text().strip(),
                                "preco": preco.inner_text().strip()
                            })
                except:
                    print(f"⚠️ Erro na página {p_num}. Amazon pode ter bloqueado ou a busca foi inválida.")

                next_btn = page.query_selector("a.s-pagination-next")
                if not next_btn: break
                next_btn.click()
                page.wait_for_timeout(3000)
            
            browser.close()

    def process_and_save(self):
        if not self.data_raw:
            print("❌ Nenhum dado coletado. Tente outro termo ou verifique sua conexão.")
            return

        df_new = pd.DataFrame(self.data_raw)
        df_new["preco"] = df_new["preco"].str.replace(r"[^\d]", "", regex=True).astype(float)
        
        # Lógica de Tier (IA de Preço)
        media_atual = df_new["preco"].mean()
        
        def definir_tier(p):
            if p < (media_atual * 0.85): return "S - Relíquia"
            elif p < (media_atual * 0.95): return "A - Ótimo Preço"
            elif p <= (media_atual * 1.05): return "B - Preço Médio"
            else: return "C - Caro"

        df_new["tier"] = df_new["preco"].apply(definir_tier)
        df_new["score_oportunidade"] = (1 - (df_new["preco"] / media_atual)).round(2)

        if os.path.exists(self.file_json):
            df_old = pd.read_json(self.file_json)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new

        df_final.to_json(self.file_json, orient="records", force_ascii=False, indent=4)
        print(f"✅ Sucesso! {len(df_new)} novos itens salvos.")

# --- LÓGICA DE INTERAÇÃO COM IA DE CORREÇÃO ---
if __name__ == "__main__":
    dicionario = ["notebook gamer", "rtx 4060", "monitor 144hz", "iphone 15"]
    
    entrada = input("🔍 O que você quer pesquisar na Amazon? ")

    # IA corrigindo erro de digitação (Fuzzy Match)
    sugestao, score = process.extractOne(entrada, dicionario)
    
    if score > 75:
        print(f"✨ IA entendeu seu erro e buscou por: '{sugestao}' (Confiança: {score}%)")
        termo_final = sugestao
    else:
        termo_final = entrada

    quer_alerta = input("🔔 Ativar alerta de promoção (S/N)? ").lower()

    analyzer = AIMarketAnalyzer(termo_final)
    analyzer.scrape_data(max_pages=2)
    analyzer.process_and_save()

    # Simulação de Alerta no terminal
    if quer_alerta == 's':
        print("\n📢 SISTEMA DE MONITORAMENTO ATIVADO!")
        print(f"Se eu encontrar um '{termo_final}' no Tier S, você verá um aviso aqui.")