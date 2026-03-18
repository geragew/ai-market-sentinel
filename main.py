from collector import AmazonCollector
from analyzer import MarketAnalyzer

def main():
    print("🚀 Iniciando o AI Market Sentinel...")
    
    # 1. Coleta os dados
    termo_busca = "notebook gamer"
    collector = AmazonCollector()
    produtos = collector.coletar_dados(termo_busca)
    
    # 2. Analisa os dados
    if produtos:
        analyzer = MarketAnalyzer(produtos)
        df_analisado = analyzer.classificar_ofertas()
        
        print("\n📊 Resumo da Análise:")
        print(df_analisado[['nome', 'preco', 'tier']].head())
        
        # Salva o resultado final
        df_analisado.to_json("market_data_history.json", orient="records", indent=4)
        print("\n✅ Dados salvos com sucesso!")
    else:
        print("❌ Nenhum dado coletado para analisar.")

if __name__ == "__main__":
    main()