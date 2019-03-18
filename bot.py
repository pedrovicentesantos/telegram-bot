import feedparser
import time 
import telegram
import os
import config

TOKEN = os.environ.get('TOKEN')
meuId = os.environ.get('meuId')

quais_enviar = []
bot = telegram.Bot(TOKEN)

# Função que checa se um feed já foi enviado

# Ou seja se ele já foi salvo no arquivo txt

def foiEnviado(entrada):
    with open(config.arquivo, 'r') as arquivo:
        for line in arquivo:
            if entrada in line:
                return True
    return False

# Função que só pega os feeds que tenho interesse
def filtrarFeeds(entrada):
    nome_insensitive = entrada[1].lower()
    if entrada[0] == config.names[0]:
        for legenda in config.legendas:
            if legenda in nome_insensitive:
                return True
    elif entrada[0] == config.names[1]:
        for serie in config.series:
#             Se for Doom Patrol eu só procuro pelo formato 720p WEBRip HEVC x265-RMTeam
            if serie == 'doom patrol':
                if (serie in nome_insensitive and config.formato[2] in nome_insensitive):
                    return True
#             Nos outros casos faço procurando pelos outros dois formatos iniciais
            else:
                if (serie in nome_insensitive and config.formato[0] in nome_insensitive) or (serie in nome_insensitive and config.formato[1] in nome_insensitive):
                    return True
    return False
            
def pegarFeeds():
    f = open(config.arquivo, 'a')
    global quais_enviar
    quais_enviar = []
    
    for url in config.urls:
        feed = feedparser.parse(url)
        
        for entrada in feed.entries:
            title = entrada.title
            link = entrada.link
            feedTitle = feed.feed.title
            data = entrada.published
            
            identificador = link+' '+data
            
            # Salvo no arquivo caso não tenha sido enviado ainda
            if not foiEnviado(identificador):
                if filtrarFeeds([feedTitle,title]):
                    quais_enviar.append([feedTitle,title,link])
                    f.write(identificador + "\n")

    f.close()          


bot.send_message(config.meuId, "Iniciando...")
while True:
    pegarFeeds()
    bot = telegram.Bot(config.TOKEN)
    for entrada in quais_enviar:
        bot.send_message(config.meuId, entrada[1] + '\n' + entrada[2])
    #  A cada 20min (60*20)
    if time.localtime().tm_hour in [21,22,23,0,1,2,3,4,5,6,7,8]:
        time.sleep(1200)
    #  A cada 1h (60*60)
    else:
        time.sleep(3600)
