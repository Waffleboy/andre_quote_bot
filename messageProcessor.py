# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 16:02:36 2016

@author: waffleboy
"""

import yagmail
from datetime import date
import logger_settings
import dbWrapper

logger = logger_settings.setupLogger().getLogger(__name__)

# Main function
def processMessage(incomingMessage,action,user_object,update):
    try:
        logger.debug("Processing incoming message with action %s",action)
        lastUsed = dbWrapper.setLastUsed(user_object.telegram_id)
        dbWrapper.addToTimesUsed(user_object.telegram_id)
        if lastUsed:
            logger.debug("Set last used for user %s",str(user_object))
        successfulAction = False
    except Exception as e:
        logger.warn("Error occurred while processing message! Probably a DB thing")
        logger.exception(e)
        update.message.reply_text("Sorry, something went wrong! Contact @waffleboy!")
        
    if action == "diaryLog":
        successfulAction = handleAction_DiaryLog(incomingMessage,user_object)
    
    # If more actions in the future
    return successfulAction
    
#==============================================================================
#                           Action Handlers
#==============================================================================

# Handle the "diaryLog" action
def handleAction_DiaryLog(incoming_message,user_object):
    logger.info("Processing action 'diaryLog' for incoming message")
    successfulAction = False
    todaysDate = date.today()
    todaysDateStr = currentStrOfTimeFormat(todaysDate)
    incoming_message = removeCommand(incoming_message,"/log")
    successfulAction = sendEmail(todaysDateStr,incoming_message,user_object)
    if successfulAction:
        logger.info("diaryLog Action successfully completed.")
    else:
        logger.warn("diaryLog Action failed to carry out.")
    return successfulAction
    
#==============================================================================
#                           Yagmail Functions
#==============================================================================
def sendEmail(todaysDate,incoming_message,user_object):
    logger.info("Sending message: %s",incoming_message)
    emailToSendFrom = user_object.getMyEmail()
    appPassword = user_object.getMyAppPassword()
    emailsToSendTo = user_object.getTargetEmails()
    overallSuccess = True 
    for email in emailsToSendTo:
        try:
            yag = yagmail.SMTP(emailToSendFrom, appPassword)
            success = yag.send(email, todaysDate, incoming_message)
            if not (success == {}):
                overallSuccess = False
        except Exception as e:
            overallSuccess = False
            logger.warn("Error with yagmail in sending message: ErrorLog: %s, Message: %s",e,incoming_message)
        if success:
            logger.info("Message successfully sent")
    return overallSuccess

#==============================================================================
#                              Misc Func
#==============================================================================
def currentStrOfTimeFormat(dateObject):
    return dateObject.strftime("%A, %d/%m/%Y")
    
def removeCommand(incoming_message,command):
    skipLength = len(command) + 1
    return incoming_message[skipLength:]