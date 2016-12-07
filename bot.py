# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 12:01:45 2016

@author: waffleboy
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
from flask import Flask
import logger_settings
import dbWrapper

app = Flask(__name__)

# Enable logging
logger = logger_settings.setupLogger().getLogger(__name__)

#==============================================================================
#                               SLASH COMMANDS
#==============================================================================

# These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.

def helpme(bot, update):
    update.message.reply_text(getHelpText())

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
def start(bot, update):
    update.message.reply_text("""
    Hi, I'm Andrebot! I'm a collection of epic Andre quotes to be preserved foreverrrrrr

Use /add <quote> to add a new epic Andre quote

Use /viewall to view a list of existing quotes

Use /get <number> to get a specific Andre quote

Use /random to get a randomly selected epic Andre quote!

Type /help to see these commands again.
""")

def add_new_quote(bot,update):
    username = update.message.from_user.username
    logger.info("Received a add_new_quote request from {}".format(username))
    update.message.reply_text("Thanks {}! Adding your quote to the Andre database..".format(username))
    quote_id = dbWrapper.add_new_quote(update)
    if quote_id:
        update.message.reply_text("Quote successfully added! Your quote ID is {}".format(quote_id))
        return
    update.message.reply_text("Quote NOT added. Quote already exists or an unforeseen error has occured.")


def view_all_andre_quotes(bot,update):
    username = update.message.from_user.username
    logger.info("Received a view_all_andre_quotes request from {}".format(username))
    update.message.reply_text("Getting quotes..")
    list_of_quotes = dbWrapper.get_all_quotes()
    if list_of_quotes:
        for quote in list_of_quotes:
            update.message.reply_text(dbWrapper.format_quote(quote))
        return
    reply_with_empty_message(update)
    
def get_quote_by_id(bot,update):
    username = update.message.from_user.username
    logger.info("Received a get_quote_by_id request from {}".format(username))
    update.message.reply_text("Getting specified quote..")
    formatted_quote = dbWrapper.get_formatted_quote_by_id(update)
    if formatted_quote:
        update.message.reply_text(formatted_quote)
        return
    update.message.reply_text("I'm unable to find a quote with that id!")
    
def random_quote(bot,update):
    update.message.reply_text("Getting a random epic Andre quote..")
    username = update.message.from_user.username
    logger.info("Received a random_quote request from {}".format(username))
    formatted_quote = dbWrapper.get_random_formatted_quote(update)
    if formatted_quote:
        update.message.reply_text(formatted_quote)
        return
    reply_with_empty_message(update)
#==============================================================================
#                               Helper Funcs
#==============================================================================

def reply_with_empty_message(update):
    update.message.reply_text("There are currently no quotes in the Andre database :( Why dont you add some?")

def getHelpText():
    s = """
    
Use /add <quote> to add a new epic Andre quote

Use /viewall to view a list of existing quotes

Use /get <number> to get a specific Andre quote

Use /random to get a randomly selected epic Andre quote!
    
For further help, contact @waffleboy
"""
    return s
    
#==============================================================================
#                                   Misc
#==============================================================================

# Standard reply upon texting the bot
def standardReply():
    s = "At the moment, I only reply to slash commands. Please try /help for more information!"
    return s

def isProductionEnvironment():
    if os.environ.get('PRODUCTION'):
        return True
    return False
    
def getUpdater():
    if isProductionEnvironment():
        logger.info("Using Production key")
        return Updater(os.environ.get("TELEGRAM_ANDREBOT_TOKEN"))
    return Updater(os.environ.get("TELEGRAM_ANDREBOT_TEST_TOKEN"))

#==============================================================================
#                                   Run
#==============================================================================
    
def main():
    logger.info("Starting Andre Bot!")
    # Create the EventHandler and pass it your bot's token.
    updater = getUpdater()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", helpme))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add_new_quote))
    dp.add_handler(CommandHandler("get", get_quote_by_id))
    dp.add_handler(CommandHandler("viewall", view_all_andre_quotes))
    dp.add_handler(CommandHandler("random", random_quote))
    
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, standardReply()))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()