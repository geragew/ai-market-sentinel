import telebot
import json
import pandas as pd
from analyzer import MarketAnalyzer

TOKEN = "8295418707:AAEJ38tqvt31EagPQkEuMG1CImFI-LCrrXg"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def processar(message):
    termo = message.text.strip()
    if termo.startswith('/'): return

    try:
        with open("market_data_history.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        analyzer = MarketAnalyzer(dados)
        analyzer.filtrar_por_nome(termo)
        df = analyzer.classificar_ofertas()

        if df.empty:
            bot.reply_to(message, "⚠️ Nada no histórico. Roda o coletor primeiro!")
            return

        # Pega os 3 melhores
        top = df.sort_values(by='preco').head(3)

        for _, row in top.iterrows():
            # Se o link for None ou vazio, a gente avisa
            link = row['link'] if row['link'] and row['link'] != "None" else "Link indisponível"
            
            msg = (
                f"🚀 *OFERTA ENCONTRADA!*\n"
                f"🏆 *Tier:* {row['tier']}\n"
                f"📦 *Produto:* {row['nome']}\n"
                f"💰 *Preço:* R$ {row['preco']:.2f}\n\n"
                f"🛒 *LINK DE COMPRA:* \n{link}"
            )
            bot.send_message(message.chat.id, msg, parse_mode="Markdown", disable_web_page_preview=False)

    except Exception as e:
        bot.reply_to(message, f"Erro: {e}")

print("🚀 Bot Online!")
bot.polling()