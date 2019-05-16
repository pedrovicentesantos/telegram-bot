import feedparser
import time 
import telegram
import os
import config

from bs4 import BeautifulSoup
import requests

import cfscrape

TOKEN = os.environ.get('TOKEN')
meuId = os.environ.get('meuId')

quais_enviar = []
bot = telegram.Bot(TOKEN)
scraper = cfscrape.create_scraper()

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
    # Se for do feed do legendas.tv
    if entrada[0] == config.urls_feeds[0]:
        for legenda in config.legendas:
            if legenda in nome_insensitive:
                return True
    # Se for do site do rmz.cr
    elif entrada[0] == config.urls_sites[0]:
        for serie in config.series_formato1:
            for formato in config.formato1:
                if (serie in nome_insensitive and formato in nome_insensitive):
                    return True
        for serie in config.series_formato2:
            for formato in config.formato2:
                if (serie in nome_insensitive and formato in nome_insensitive):
                    return True
    return False
            
def pegarFeeds():
    f = open(config.arquivo, 'a')
    global quais_enviar
    quais_enviar = []
    
    # Caso seja feito pelo feed
    for url in config.urls_feeds:
        feed = feedparser.parse(url)
        
        for entrada in feed.entries:
            title = entrada.title
            link = entrada.link
            feedLink = feed.feed.subtitle_detail.base
            data = entrada.published
            
            identificador = link+' '+data
            
            # Salvo no arquivo caso não tenha sido enviado ainda
            if not foiEnviado(identificador):
                if filtrarFeeds([feedLink,title]):
                    quais_enviar.append([title,link])
                    f.write(identificador + "\n")

    # Caso seja feito por web scraping
    for url in config.urls_sites:
        try:
            resposta = scraper.get(url)
            dados = resposta.text
            soup = BeautifulSoup(dados, 'lxml')
            
            #Pego cada um dos links para os episodios dentro da caixa Latest Episodes
            episodios = soup.select('.epicontainer ul li span .episize a')

            for episodio in episodios:
                titulo = episodio.get('title')
                # O link só vem com o pedaço final, por isso preciso somar a url
                link = url + episodio.get('href')
                if not foiEnviado(link):
                    if filtrarFeeds([url,titulo]):
                        quais_enviar.append([titulo,link])
                        f.write(link + "\n")
        except:
            bot.send_message(meuId, resposta)

    f.close()          


bot.send_message(meuId, "Iniciando...")
while True:
    pegarFeeds()
    bot = telegram.Bot(TOKEN)
    for entrada in quais_enviar:
        bot.send_message(meuId, entrada[0] + '\n' + entrada[1])
    #  A cada 20min (60*20)
    # if time.localtime().tm_hour in [21,22,23,0,1,2,3,4,5,6,7,8]:
        # time.sleep(1200)
    #  A cada 1h (60*60)
    # else:
    # A cada 1h sempre
    time.sleep(3600)
