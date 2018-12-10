import feedparser
from subprocess import check_output
import time 
import sys
import threading
import requests
import telegram
import json
import config
import os
import psycopg2

TOKEN = os.environ.get('TOKEN')
meuId = os.environ.get('meuId')
DATABASE_URL = os.environ['DATABASE_URL']

bot = telegram.Bot(TOKEN)

def conectarDb():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except:
        bot.send_message(meuId, "Não consegui conectar no BD")

def post_is_in_db(link):
    with open(config.db, 'r') as database:
        for line in database:
            if link in line:
                return True
    return False

def filtrarFeeds(post):
    if post[0]==config.names[0]:
        for dublado in config.dublados:
            if dublado in post[1]:
                return True
    elif post[0]==config.names[1]:
        for serie in config.series:
            if serie in post[1]:
                return True
    elif post[0]==config.names[2]:
        for serie in config.series:
            if serie in post[1] and config.formato[0] in post[1] and config.formato[1] in post[1]:
                return True
    elif post[0]==config.names[3]:
        for legendado in config.legendados:
            if legendado in post[1]:
                return True
    return False
            
#
# get the feed data from the url
#
def getFeeds():
    f = open(config.db, 'a')
    global posts_to_print
    posts_to_print = []
    try:
        response = requests.get(config.yts,params=config.parameters)
        data=response.json()
        for dado in data["data"]["movies"]:
            feedTitle=config.names[3]
            title=dado["title"]
            link=dado["url"]
            if not post_is_in_db(link):
                if filtrarFeeds([feedTitle,title,link]):
                    posts_to_print.append([feedTitle,title,link])
                    f.write(link + "\n")
    except:
        pass
    #     bot.send_message(meuId, "Erro na API YTS")
    
    for url in config.urls:
        feed = feedparser.parse(url)
        #
        # figure out which posts to print

        for post in feed.entries:
            # if post is already in the database, skip it
            title = post['title']
            link = post['link']
            feedTitle = feed.feed.title
            if not post_is_in_db(link):
                if filtrarFeeds([feedTitle,title,link]):
                    posts_to_print.append([feedTitle,title,link])
                    f.write(link + "\n")

    f.close()          
    #return posts_to_print

#getFeeds()

startTime=time.time()
bot.send_message(meuId, "Iniciando...")
while True:
    getFeeds()
    if (len(posts_to_print) > 0):
        conn = conectarDb()
        for post in posts_to_print:
            bot.send_message(meuId, post[0]+"\n\n"+post[1]+'\n'+post[2])
    conn.close()
    time.sleep(300.0 - ((time.time() - startTime) % 60.0))