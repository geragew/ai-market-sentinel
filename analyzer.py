import pandas as pd
from thefuzz import process

class MarketAnalyzer:
    def __init__(self, dados_produtos):
        self.df = pd.DataFrame(dados_produtos)

    def filtrar_por_nome(self, termo_busca, threshold=60):
        """Usa IA (Fuzzy Matching) para garantir que o produto é o correto"""
        nomes_encontrados = self.df['nome'].tolist()
        # Encontra as melhores correspondências
        matches = process.extract(termo_busca, nomes_encontrados, limit=len(nomes_encontrados))
        
        # Filtra apenas os que têm pontuação acima do limite (threshold)
        nomes_validos = [match[0] for match in matches if match[1] >= threshold]
        self.df = self.df[self.df['nome'].isin(nomes_validos)].copy()
        return self.df

    def classificar_ofertas(self):
        """Classifica os produtos em Tiers baseados no preço médio"""
        if self.df.empty:
            return self.df
            
        preco_medio = self.df['preco'].mean()
        
        def definir_tier(preco):
            if preco < preco_medio * 0.8:
                return 'Tier S (Relíquia)'
            elif preco < preco_medio * 1.1:
                return 'Tier A (Preço Justo)'
            else:
                return 'Tier C (Caro)'
        
        self.df['tier'] = self.df['preco'].apply(definir_tier)
        return self.df