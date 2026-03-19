import telebot # Certifique-se de ter dado pip install pyTelegramBotAPI


TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telebot.TeleBot(TOKEN)


class AIMarketAnalyzer:

    def __init__(self, dados):
        self.df = pd.DataFrame(dados)
        self.df_filtrado = pd.DataFrame()
 

@bot.message_handler(commands=['start', 'oi'])
def boas_vindas(message):
    bot.reply_to(message, "🚨 SENTINEL v6 ATIVO! 🚨\n\nDog, o que você quer que eu monitore na Amazon agora? Manda o nome!")

@bot.message_handler(func=lambda message: True)
def processar_analise_automatica(message):
    termo = message.text
    bot.send_message(message.chat.id, f"⚙️ Analisando histórico para: {termo.upper()}...")
    
    # Carrega os dados 
    file_path = "market_data_history.json"
    if not os.path.exists(file_path):
        bot.send_message(message.chat.id, "❌ Banco de dados não encontrado!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # Roda IA
    analyzer = AIMarketAnalyzer(dados)
    analyzer.filtrar_por_nome(termo)
    df_final = analyzer.classificar_ofertas()

    if df_final.empty:
        bot.send_message(message.chat.id, f"⚠️ Nada de relevante para '{termo}'.")
    else:
        # Pega a melhor oferta (Relíquia)
        melhor = df_final.sort_values(by='preco').iloc[0]
        msg = (f"💎 *MELHOR OPORTUNIDADE:* \n\n"
               f"📦 {melhor['produto']}\n"
               f"💰 *Preço:* R$ {melhor['preco']:.2f}\n"
               f"🏷️ *Status:* {melhor['tier']}")
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
        
        # Salva o JSON pro Power BI atualizar
        df_final.to_json("market_data_analisado.json", orient="records", indent=4)

if __name__ == "__main__":
    # Se for rodar no PC pra testar o "Oi", use:
    bot.polling()
