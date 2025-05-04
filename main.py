import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import json
import os
pontuacao = {}

def carregar_pontuacao():
    global pontuacao
    if os.path.exists("pontuacao.json"):
        with open("pontuacao.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
            # Converte chaves para int e garante formato atualizado
            pontuacao = {}
            for k, v in dados.items():
                user_id = int(k)
                if isinstance(v, int):
                    # formato antigo, só tinha número
                    pontuacao[user_id] = {
                        "nome": f"Usuário {user_id}",
                        "pontos": v,
                        "nivel": 1
                    }
                else:
                    pontuacao[user_id] = v

carregar_pontuacao()

API_TOKEN = '8146659975:AAEm_IacSosvWBnK9hQ4A4TeYVuccNqofto'
bot = telebot.TeleBot(API_TOKEN)

def salvar_pontuacao():
    global pontuacao
    with open("pontuacao.json", "w", encoding="utf-8") as f:
        json.dump(pontuacao, f, ensure_ascii=False, indent=2)

perguntas_quiz = [
    {
        "pergunta": "🎯 Qual jogador é um dos fundadores da FURIA?",
        "opcoes": ["FalleN", "Guerri", "Yuurih", "Chelo"],
        "correta": "Guerri"
    },
    {
        "pergunta": "💥 Em qual campeonato internacional a FURIA chegou nas semifinais em 2022?",
        "opcoes": ["ESL One Cologne", "PGL Major Antwerp", "IEM Katowice", "BLAST Premier Spring"],
        "correta": "PGL Major Antwerp"
    },
    {
        "pergunta": "📅 Em que ano foi fundada a FURIA?",
        "opcoes": ["1997", "2000", "2017", "2020"],
        "correta": "2017"
    },
    {
        "pergunta": "🎮 Em qual jogo a FURIA começou sua história?",
        "opcoes": ["LoL", "CS:GO", "Valorant", "PUBG"],
        "correta": "CS:GO"
    },
    {
        "pergunta": "🌍 Qual é o país de origem da FURIA?",
        "opcoes": ["Brasil", "EUA", "Argentina", "Portugal"],
        "correta": "Brasil"
    },
    {
        "pergunta": "🐆 Qual é o mascote da FURIA?",
        "opcoes": ["Pantera", "Leão", "Tigre", "Cachorro"],
        "correta": "Pantera"
    },
    {
        "pergunta": "🧢 Qual marca de boné já patrocinou a FURIA?",
        "opcoes": ["New Era", "Nike", "Adidas", "Puma"],
        "correta": "New Era"
    }
]

def voltar_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 Voltar ao menu", callback_data="menu"))
    return markup

@bot.message_handler(commands=['start', 'help'])
def start(msg):
    bot.reply_to(msg, '''👊 *Salve, torcedor da FURIA!*
Use /menu pra ver tudo que posso fazer!
Use /quiz pra testar seus conhecimentos!
Use /pontuacao pra ver seus pontos.''', parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['bom_dia'])
def bom_dia(msg):
    bot.reply_to(msg, '🌞 *Bom dia, guerreiro(a) da FURIA!*', parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['grita'])
def grita(msg):
    bot.reply_to(msg, '🔊 VAAAAAI FURIAAAA!!! 🐆🔥', parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['fala_furia'])
def fala_furia(msg):
    frases = [
        "Aqui é FURIA, porra!",
        "Joga com sangue nos olhos!",
        "Quem enfrenta, cai!",
    ]
    escolha = random.choice(frases)
    bot.reply_to(msg, escolha, reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['quiz'])
def quiz(msg):
    enviar_pergunta_quiz(msg.chat.id, msg.from_user.id)

def enviar_pergunta_quiz(chat_id, user_id):
    pergunta = random.choice(perguntas_quiz)
    texto = pergunta["pergunta"]

    markup = InlineKeyboardMarkup()
    for opcao in pergunta["opcoes"]:
        data = f"quiz|{user_id}|{pergunta['correta']}|{opcao}"
        markup.add(InlineKeyboardButton(opcao, callback_data=data))

    bot.send_message(chat_id, f"❓ *{texto}*", parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz|"))
def responder_quiz(call):
    global pontuacao
    parts = call.data.split("|")
    if len(parts) != 4:
        return
    _, user_id, correta, escolhida = parts
    user_id = int(user_id)

    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Essa pergunta não é sua!")
        return

    if escolhida == correta:
        nome = call.from_user.first_name

        if user_id in pontuacao:
            pontuacao[user_id]["pontos"] += 1
        else:
            pontuacao[user_id] = {
                "nome": nome,
                "pontos": 1,
                "nivel": 1
            }

        salvar_pontuacao()

        bot.answer_callback_query(call.id, "✅ Acertou, monstro!")
        bot.send_message(call.message.chat.id, f"🔥 *Acertou!* A resposta certa era mesmo *{correta}*.", parse_mode='Markdown')
    else:
        bot.answer_callback_query(call.id, "❌ Errou!")
        bot.send_message(call.message.chat.id, f"😬 *Errou!* A resposta certa era *{correta}*.", parse_mode='Markdown')

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Outra pergunta", callback_data="quiz"),
        InlineKeyboardButton("Voltar para o menu", callback_data="menu")
    )
    bot.send_message(call.message.chat.id, "O que você quer fazer agora?", reply_markup=markup)

@bot.message_handler(commands=['pontuacao'])
def mostrar_pontuacao_cmd(msg):
    mostrar_pontuacao_usuario(msg.from_user.id, msg.chat.id)
    dados = pontuacao.get(user_id, {"nome": "Desconhecido", "pontos": 0, "nivel": 1})
    nome = dados["nome"]
    pontos = dados["pontos"]
    nivel = dados["nivel"]

    def nivel_para_texto(nivel):
        if nivel <= 2:
            return "Iniciante"
        elif nivel <= 4:
            return "Aprendiz"
        elif nivel <= 6:
            return "Veterano"
        elif nivel <= 9:
            return "Imparável"
        else:
            return "Furioso"

    texto = f"📊 *{nome}*, você tem *{pontos}* ponto(s)\n🏅 Nível: *{nivel_para_texto(nivel)}*"
    bot.send_message(chat_id, texto, parse_mode='Markdown', reply_markup=voltar_menu_markup())


@bot.callback_query_handler(func=lambda call: call.data == "pontuacao")
def pontuacao_callback(call):
    mostrar_pontuacao_usuario(call.from_user.id, call.message.chat.id)
    bot.send_message(call.message.chat.id, f"📊 *Sua pontuação atual:* {pontos} ponto(s)", parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.callback_query_handler(func=lambda call: call.data == "torcida")
def torcida_callback(call):
    bot.send_message(call.message.chat.id, "🔊 VAAAAAI FURIAAAA!!! 🐆🔥", parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['fala_furia'])
def fala_furia(msg):
    frases = [
        "Aqui é FURIA, porra!",
        "Joga com sangue nos olhos!",
        "Quem enfrenta, cai!",
    ]
    escolha = random.choice(frases)
    bot.reply_to(msg, escolha, reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['quiz'])
def quiz(msg):
    enviar_pergunta_quiz(msg.chat.id, msg.from_user.id)

def enviar_pergunta_quiz(chat_id, user_id):
    pergunta = random.choice(perguntas_quiz)
    texto = pergunta["pergunta"]

    markup = InlineKeyboardMarkup()
    for opcao in pergunta["opcoes"]:
        data = f"quiz|{user_id}|{pergunta['correta']}|{opcao}"
        markup.add(InlineKeyboardButton(opcao, callback_data=data))

    bot.send_message(chat_id, f"❓ *{texto}*", parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz|"))
def responder_quiz(call):
    _, user_id, correta, escolhida = call.data.split("|")
    user_id = int(user_id)

    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Essa pergunta não é sua!")
        return

    if escolhida == correta:
        pontuacao[user_id] = pontuacao.get(user_id, 0) + 1
        salvar_pontuacao()
        bot.answer_callback_query(call.id, "✅ Acertou, monstro!")
        bot.send_message(call.message.chat.id, f"🔥 *Acertou!* A resposta certa era mesmo *{correta}*.", parse_mode='Markdown')
    else:
        bot.answer_callback_query(call.id, "❌ Errou!")
        bot.send_message(call.message.chat.id, f"😬 *Errou!* A resposta certa era *{correta}*.", parse_mode='Markdown')

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("Outra pergunta", callback_data="quiz"),
        InlineKeyboardButton("Voltar para o menu", callback_data="menu")
    )
    bot.send_message(call.message.chat.id, "O que você quer fazer agora?", reply_markup=markup)

def mostrar_pontuacao_usuario(user_id, chat_id):
    dados = pontuacao.get(user_id, {"nome": "Desconhecido", "pontos": 0, "nivel": 1})
    nome = dados["nome"]
    pontos = dados["pontos"]
    nivel = dados["nivel"]

    def conquista_para_texto(pontos):
        if pontos >= 5:
            return "👑 *Lenda da FURIA*"
        elif pontos >= 3:
            return "🔥 *FURIOSO em Ascensão*"
        elif pontos >= 1:
            return "👶 *Iniciante FURIOSO*"
        else:
            return "❌ *Ainda sem conquistas*"

    conquista = conquista_para_texto(pontos)

    texto = (
        f"📊 *{nome}*, você tem *{pontos}* ponto(s)\n"
        f"🥇 Conquista: {conquista}"
    )
    bot.send_message(chat_id, texto, parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['ranking'])
def mostrar_ranking(msg):
    global pontuacao
    if not pontuacao:
        bot.send_message(msg.chat.id, "Ainda não há pontuações registradas.")
        return

    top = sorted(pontuacao.items(), key=lambda x: x[1]["pontos"], reverse=True)[:5]
    texto = "🏆 *Ranking dos FURIOSOS:*\n\n"

    for i, (user_id, dados) in enumerate(top, start=1):
        nome = dados["nome"]
        pontos = dados["pontos"]

        if pontos < 5:
            nivel = "Novato"
        elif pontos < 10:
            nivel = "Dedicado"
        elif pontos < 20:
            nivel = "Raiz"
        else:
            nivel = "Furioso"

        texto += f"{i}º - *{nome}* — {pontos} ponto(s) 🏅 _{nivel}_\n"

    bot.send_message(msg.chat.id, texto, parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(commands=['redes'])
def redes_sociais(msg):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Instagram", url="https://www.instagram.com/furiagg/"),
        InlineKeyboardButton("Twitter", url="https://twitter.com/furiagg"),
        InlineKeyboardButton("YouTube", url="https://www.youtube.com/@furiagg")
    )
    markup.add(InlineKeyboardButton("🔙 Voltar ao menu", callback_data="menu"))
    bot.send_message(msg.chat.id, "🌐 Redes sociais da FURIA:", reply_markup=markup)

@bot.message_handler(commands=['loja'])
def loja_furia(msg):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("🛒 Acessar o site oficial da FURIA", url="https://www.furia.gg/"),
        InlineKeyboardButton("🔙 Voltar ao menu", callback_data="menu")
    )
    bot.send_message(msg.chat.id, "🔥 Confira os produtos e novidades no site oficial:", reply_markup=markup)

@bot.message_handler(commands=['menu'])
def menu(msg):
    abrir_menu(msg.chat.id)

def abrir_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Quiz", callback_data="quiz"),
        InlineKeyboardButton("Pontuação", callback_data="pontuacao"),
        InlineKeyboardButton("Torcida", callback_data="torcida"),
        InlineKeyboardButton("Próximos Jogos", callback_data="jogos"),
        InlineKeyboardButton("Redes Sociais", callback_data="redes"),
        InlineKeyboardButton("Loja Oficial", callback_data="loja"),
        InlineKeyboardButton("Promoção Camiseta", callback_data="promocao"),
        InlineKeyboardButton("Ranking", callback_data="ranking")
        )
    bot.send_message(chat_id, "📋 *Menu da FURIA:*", parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def responder_botoes(call):
    if call.data == "torcida":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, '🔊 VAAAAAI FURIAAAA!!! 🐆🔥', parse_mode='Markdown', reply_markup=voltar_menu_markup())
    elif call.data == "quiz":
        enviar_pergunta_quiz(call.message.chat.id, call.from_user.id)
    elif call.data == "pontuacao":
        mostrar_pontuacao_usuario(call.from_user.id, call.message.chat.id)
    elif call.data == "jogos":
        proximos_jogos(call.message)
    elif call.data == "redes":
        redes_sociais(call.message)
    elif call.data == "loja":
        loja_furia(call.message)
    elif call.data == "menu":
        abrir_menu(call.message.chat.id)
    elif call.data == "ranking":
        mostrar_ranking(call.message)
    elif call.data == "promocao":
        texto = (
            "🔥 *CAMISA OFICIAL FURIA - FUTURE IS BLACK* 🔥\n\n"
            "💥 Promoção exclusiva: *R$ 139,00* na loja oficial!\n"
            "Mostre sua garra com o uniforme mais insano da temporada.\n\n"
            "🛒 [Clique aqui para comprar agora](https://www.furia.gg/produto/camiseta-furia-future-is-black-preta-150146)\n\n"
            "⚠️ *Oferta por tempo limitado!*"
        )
        with open("camisa_furia.png", "rb") as photo:
            bot.send_photo(call.message.chat.id, photo=photo, caption=texto, parse_mode='Markdown', reply_markup=voltar_menu_markup())

def get_proximos_jogos_lol():
    return [
        "📅 05/05 às 18:00 – FURIA vs RED Canids (CBLOL)",
        "📅 11/05 às 16:30 – FURIA vs LOUD (CBLOL)"
    ]

def get_proximos_jogos_cs():
    return [
        "📅 06/05 às 21:00 – FURIA vs NAVI (IEM Dallas)",
        "📅 13/05 às 19:00 – FURIA vs G2 (BLAST Premier)"
    ]

def get_proximos_jogos_kings():
    return [
        "📅 07/05 às 20:00 – FURIA Kings vs Camisa 10 (Kings League Brasil)",
        "📅 14/05 às 17:45 – FURIA Kings vs G3X Legacy (Kings League Brasil)"
    ]

@bot.message_handler(commands=['proximos_jogos'])
def proximos_jogos(msg):
    jogos_lol = get_proximos_jogos_lol()
    jogos_cs = get_proximos_jogos_cs()
    jogos_kings = get_proximos_jogos_kings()

    resposta = "🎮 *Próximos jogos da FURIA:*\n\n"
    resposta += "🧠 *League of Legends:*" + "\n".join(jogos_lol) + "\n\n"
    resposta += "🔫 *Counter-Strike 2:*" + "\n".join(jogos_cs) + "\n\n"
    resposta += "👑 *Kings League Brasil:*" + "\n".join(jogos_kings)

    bot.reply_to(msg, resposta, parse_mode='Markdown', reply_markup=voltar_menu_markup())

@bot.message_handler(func=lambda msg: True)
def resposta_padrao(msg):
    abrir_menu(msg.chat.id)

bot.infinity_polling()