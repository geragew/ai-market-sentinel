import pandas as pd
import os
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

class AIMarketAnalyzer:
    def __init__(self, search_term="notebook gamer"):
        self.base_url = "https://www.amazon.com.br"
        self.search_term = search_term
        self.file_json = "market_data_history.json"
        self.data_raw = []

    def scrape_data(self, max_pages=1):
        print(f"🚀 Iniciando coleta para: {self.search_term}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            
            page.goto(self.base_url)
            page.fill("#twotabsearchtextbox", self.search_term)
            page.keyboard.press("Enter")
            
            page.wait_for_timeout(5000) 

            for p_num in range(1, max_pages + 1):
                print(f"📦 Capturando página {p_num}...")
                try:
                    page.wait_for_selector("div[data-component-type='s-search-result']", timeout=10000)
                    cards = page.query_selector_all("div[data-component-type='s-search-result']")

                    for card in cards:
                        titulo_el = card.query_selector("h2 span")
                        preco_el = card.query_selector(".a-price-whole")
                        
                        # --- SELETOR DE LINK REFORÇADO ---
                        # Procuramos qualquer link dentro do card que leve para um produto (/dp/)
                        link_el = card.query_selector("a[href*='/dp/']")
                        
                        if titulo_el and preco_el:
                            href = link_el.get_attribute("href") if link_el else ""
                            
                            # Limpa o link para tirar rastreadores e garantir que seja absoluto
                            if href:
                                if href.startswith("/"):
                                    link_final = "https://www.amazon.com.br" + href.split("?")[0]
                                else:
                                    link_final = href.split("?")[0]
                            else:
                                link_final = "Link indisponível"

                            self.data_raw.append({
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "termo_busca": self.search_term,
                                "produto": titulo_el.inner_text().strip(),
                                "preco": preco_el.inner_text().strip(),
                                "link": link_final # Agora vai vir o link real
                            })
                except Exception as e:
                    print(f"⚠️ Erro na captura: {e}")

                next_btn = page.query_selector("a.s-pagination-next")
                if not next_btn or p_num >= max_pages: break
                next_btn.click()
                page.wait_for_timeout(3000)
            
            browser.close()

    def process_and_save(self):
        if not self.data_raw: return
        df_new = pd.DataFrame(self.data_raw)
        df_new["preco"] = df_new["preco"].str.replace(r"[^\d]", "", regex=True).astype(float)
        
        # Filtro Universal (Tira as capinhas)
        topo = df_new["preco"].max()
        if topo > 500:
            df_new = df_new[df_new["preco"] >= (topo * 0.4)]

        if os.path.exists(self.file_json):
            df_old = pd.read_json(self.file_json)
            df_final = pd.concat([df_old, df_new], ignore_index=True).drop_duplicates(subset=['produto', 'preco'], keep='last')
        else:
            df_final = df_new

        df_final.to_json(self.file_json, orient="records", force_ascii=False, indent=4)
        print(f"✅ Sucesso! Banco de dados atualizado com links reais.")

if __name__ == "__main__":
    entrada = input("🔍 O que vamos caçar? ")
    analyzer = AIMarketAnalyzer(entrada)
    analyzer.scrape_data()
    analyzer.process_and_save()