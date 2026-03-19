import pandas as pd

class MarketAnalyzer:
    def __init__(self, dados_produtos):
        self.df = pd.DataFrame(dados_produtos)
        if 'produto' in self.df.columns:
            self.df = self.df.rename(columns={'produto': 'nome'})

    def filtrar_por_nome(self, termo_busca):
        if self.df.empty: 
            return self.df # Garante que retorna o DF vazio em vez de None
        
        palavras_busca = termo_busca.lower().split()
        
        def validar_nome(nome):
            nome_lower = str(nome).lower()
            return all(palavra in nome_lower for palavra in palavras_busca)

        self.df = self.df[self.df['nome'].apply(validar_nome)].copy()
        
        if self.df.empty: 
            return self.df

        # FILTRO DE RELEVÂNCIA (O mata-capinha universal)
        topo_mercado = self.df['preco'].max()
        
        # Só filtra se houver uma diferença gritante (ex: algo acima de 500 reais)
        if topo_mercado > 500:
            limite_corte = topo_mercado * 0.4 
            self.df = self.df[self.df['preco'] >= limite_corte]
        
        return self.df # <-- ESSENCIAL: Retornar os dados filtrados

    def classificar_ofertas(self):
        if self.df.empty: 
            return self.df
        
        self.df['preco_unitario'] = self.df['preco']
        media_real = self.df['preco_unitario'].mean()
        
        def definir_tier(preco):
            if preco < media_real * 0.90: return 'S - Relíquia'
            elif preco < media_real * 1.05: return 'A - Justo'
            else: return 'C - Caro'

        self.df['tier'] = self.df['preco_unitario'].apply(definir_tier)
        return self.df # <-- ESSENCIAL: Retornar os dados classificados