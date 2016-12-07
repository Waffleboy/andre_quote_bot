# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 21:48:02 2016

@author: waffleboy
"""

import os,datetime
import logger_settings
import random
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String,DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logger_settings.setupLogger().getLogger(__name__)
Base = declarative_base()
engine = create_engine(os.environ["ANDREBOT_DB"])

""" DB Models """
class Quote(Base):
    __tablename__ = 'quotes'
    id = Column(Integer, primary_key=True)
    added_by = Column(String,index=True)
    added_by_telegram_id = Column(Integer,index=True)
    quote = Column(String)
    times_quoted = Column(Integer,default = 0)
    properties = Column(JSONB,default = {"last_used_details":{}})
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return "<Quote(name='%s', telegram_id='%s' quote_number='%s' added_on='%s' times_quoted = '%s')>" % (
                         self.added_by, self.added_by_telegram_id, self.id, 
                         self.created_at, self.times_quoted)
    
    def get_quote_formatted(self):
        quote = self.get_quote_raw()
        formatted_quote = format_quote(quote)
        return formatted_quote
    
    def get_formatted_creation_date(self):
        date = self.format_date(self.created_at)
        return date
        
    def get_last_quoted_on_details(self):
        usage = self.properties["last_used_details"]
        return usage
    
    def get_added_by(self):
        return self.added_by

    def get_times_quoted(self):
        return self.times_quoted
    
    def get_quote_raw(self):
        return self.quote
        
    def format_date(self,date):
        return date.date()

    
#Base.metadata.drop_all(engine)                         
#Base.metadata.create_all(engine)

#==============================================================================
#                           Wrapper Functions
#==============================================================================
    
def add_new_quote(update):
    username = update.message.from_user.username
    telegram_id = update.message.from_user.id
    quote = remove_command(update.message.text,"/add")
    session = generateSession()
    try:
        new_quote = Quote(added_by = username, 
                        added_by_telegram_id = telegram_id,
                        quote = quote)
   
        session.add(new_quote)
        session.commit()
        quote_id = new_quote.id
        session.close()
        logger.info("Successfully added quote from id %s and username %s",telegram_id,username)
    except Exception as e:
        #update.message.reply_text("Failed to save your information! Contact @Waffleboy for help")
        logger.critical("Fail to save quote information into database! Error log: %s",e)
        return False
    return quote_id
    
def get_formatted_quote_by_id(update):
    text = (update.message.text).rstrip().strip()
    quote_id = remove_command(text,"/get")
    logger.info("Message is {}".format(quote_id))
    username = update.message.from_user.username
    if quote_id.isdigit():
        formatted_quote = get_quote_and_set_last_used_and_close(quote_id,username)
        return formatted_quote
    return False


def get_random_formatted_quote(update):
    total_rows = get_number_of_rows()
    username = update.message.from_user.username
    if total_rows >= 1:
        random_number = random.randint(1,total_rows)
        formatted_quote = get_quote_and_set_last_used_and_close(random_number,username)
        return formatted_quote
    return False

def get_quote_and_set_last_used_and_close(quote_id,username):
    quote_object,session = get_quote_object_by_id(quote_id)
    formatted_quote = format_quote(quote_object)
    quote_object = update_times_and_last_used(quote_object,username)
    session.add(quote_object)
    commitAndCloseSession(session)
    return formatted_quote
#==============================================================================
#                            Misc Helpers
#==============================================================================

#FIXME: Quoted on not working
def format_quote(quote):
#    last_quoted_on = quote.get_last_quoted_on_details()
#    if last_quoted_on.get("date"):
#        date = quote.format_date(last_quoted_on["date"])
#    else:
#        date = "Never"
    return "{} \n - Andre, {} \n This quote has been quoted {} times".format(quote.quote,
                                                                               quote.get_formatted_creation_date(),
                                                                                quote.get_times_quoted())
def get_quote_object_by_id(quote_id):
    session = generateSession()
    quote_object = session.query(Quote).filter(Quote.id == quote_id).first()
    return quote_object,session
    
def update_times_and_last_used(quote_object,username):
    quote_object = add_to_times_used(quote_object)
    quote_object = update_last_used(username,quote_object)
    return quote_object
    
def remove_command(text,command):
    return text[len(command)+1:]
    
def get_number_of_rows():
    session = generateSession()
    rows = session.query(Quote).count()
    session.close()
    return rows
    
def get_all_quotes():
    session = generateSession()
    quotes = session.query(Quote).all()
    session.close()
    return quotes
    
def add_to_times_used(quote_object):
    quote_object.times_quoted += 1
    return quote_object

#FIXME: Its not saving for some reason
def update_last_used(username,quote_object):
    last_used_details = quote_object.properties["last_used_details"]
    last_used_details["date"] = datetime.datetime.utcnow()
    last_used_details["name"] = username
    quote_object.properties = {"last_used_details": last_used_details}
    return quote_object
    
def generateSession(expire_on_commit = True):
    Session = sessionmaker(bind=engine)
    session = Session()
    if expire_on_commit == False:
        session.expire_on_commit = False
    return session

def commitAndCloseSession(session):
    session.commit()
    session.close()