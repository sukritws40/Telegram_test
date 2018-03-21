#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import urllib2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json
from datetime import datetime

from mongodb_alana.history import History
from mongodb_alana.ner_db import Ner_db

BUCKET_URL = "http://localhost:5000"
history = History(os.path.abspath('mongodb_alana/mongo_info.json'))
ner = Ner_db(os.path.abspath('mongodb_alana/mongo_info.json'))



#JSON thingy
#-------------------------------------------------------------

first = True
data = {}
data['session'] = []

data2 = {
   'name' : 'ACME',
   'shares' : 100,
   'price' : 542.23
}


#-------------------------------------------------------------
def get_answer(question, session_id, conf_score):
    timestamp = datetime.now()

    # If session_id not in the db start a new session
    if history.find_session_id(session_id) is None:
        history.start_db_session(session_id)
        ner.start_db_ner(session_id)

    # write the user utterance to db
    history.update_db(session_id, 'user', question)

    utterance = urllib2.quote(question)
    print("utterance: ", utterance)

    # Forward question to bucket and get the response
    print('{}?q={}&sid={}&cs={}'.format(BUCKET_URL, utterance, session_id, conf_score))
    speech_output = json.loads(
        urllib2.urlopen('{}?q={}&sid={}&cs={}'.format(BUCKET_URL, utterance, session_id, conf_score)).read())
    # write the system utterance to db
    history.update_db(session_id, "system", speech_output[1], str(speech_output[0]), speech_output[2])
    # if news were selected (with news_id), save that to mt_newsAPI table
    if len(speech_output) > 3:
        history.update_news_id(session_id, speech_output[3])
    
    return speech_output[1], speech_output[2]

def cli():
    session_id = 'CLI-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    while True:
        question = sys.stdin.readline()
        print 'Alana: ', get_answer(question, session_id, '1.0')
        print
        if not question:
            break  # exit on empty line

#############################################################
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi, I am Alana, a conversation agent that are developed on top of Amazon Alexa Challenge 2017 winner. Alana is not perfect so please do not abuse her and do follow along the context. I hope you will hava a good time with Alana PS.This is the original Alana that we aim to develop, the more up-to date Alana will be available soon\n\nDisclaimer: Your information will not be shared.')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('There is no help!')



def echo(bot, update):
    global first
    
    """Echo the user message."""
    chat_id = update.message.chat_id
    session_id = 'CLI-' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    question = update.message.text
    answer = get_answer(question, session_id, '1.0')
    update.message.reply_text(answer[0])

   # if(first == True):
  #      data['session'].append({'Id': chat_id, 'turns':[]})
 #       chat
#        first = False
#    data['session'][0]['turns'].append({'fuck':'you', 'u': '2','Id': chat_id})

    data['session'].append({'ChatId': chat_id,'User': question, 'Alana':answer[0]})
    with open('data.json', 'w') as f:
        json.dump(data, f)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def id(bot, update):
    chat_id = update.message.chat_id
    update.message.reply_text(update.message.chat_id)


def main():
    

    
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("548018861:AAFDFAbz4ypEr-blm5f68KucXCzoPRdNNcQ")
   
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("id", id))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    


#Alana
#548018861:AAFDFAbz4ypEr-blm5f68KucXCzoPRdNNcQ
#Rob
#479000953:AAElg31XFfkxmmNOx7OD0gr98VB1-lUMbN4
#Susan
#520423425:AAEqZwKyb-sYPVpMkOTxVsBKCfqS5TLnNLk
    


#############################################################


if __name__ == '__main__':
    #cli()
    main()


