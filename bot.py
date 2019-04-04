import feedparser
import time 
import telegram
import os
import config

from bs4 import BeautifulSoup
import requests

TOKEN = os.environ.get('TOKEN')
meuId = os.environ.get('meuId')

quais_enviar = []
bot = telegram.Bot(TOKEN)

# Para fazer a conexão com o site do rmz quando ele usa a proteção ddos
headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
'Connection': 'keep-alive',
'Cookie': '__cfduid=d5459990e66ed72f7c7747e5264bc0e501541383850; HstCfa1606961=1541383851274; _ga=GA1.2.1275006512.1541383851; __dtsu=1EE70445C172465CD14B4E4702BBB269; HstCmu1606961=1552150651892; _gid=GA1.2.226368552.1554172346; rms3=a%3A5%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2235e85a833cb78551a6436e7ce11e0f94%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A14%3A%22189.122.241.31%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A120%3A%22Mozilla%2F5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F69.0.3497.100+Safari%2F537.36+OPR%2F%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1554342426%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3B%7D837bf835c884d47ed12b4c252bfea5f706462e9b; HstCnv1606961=168; HstCla1606961=1554345559995; HstPn1606961=3; HstPt1606961=538; HstCns1606961=220; cf_clearance=222c96e72f94fb073d5740f3669a482139c23ae5-1554347142-3600-150',
'Host': 'rmz.cr',
'Referer': 'http://rmz.cr/',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.127'
}

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
            resposta = requests.get(url, headers = headers)
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
            pass

    f.close()          


bot.send_message(meuId, "Iniciando...")
while True:
    pegarFeeds()
    bot = telegram.Bot(TOKEN)
    for entrada in quais_enviar:
        bot.send_message(meuId, entrada[0] + '\n' + entrada[1])
    #  A cada 20min (60*20)
    if time.localtime().tm_hour in [21,22,23,0,1,2,3,4,5,6,7,8]:
        time.sleep(1200)
    #  A cada 1h (60*60)
    else:
        time.sleep(3600)
