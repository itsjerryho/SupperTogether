# import
from telegram.ext import Updater, CommandHandler
from Helpers.PreOrderingStage import addPreOrderHandlersTo
from Helpers.OrderingStage import addOrderHandlersTo
from Helpers.StoreInterface import StoreMode
from Helpers.Data import menu
from multiprocessing import Queue

import logging
#Loggin and errors
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level = logging.INFO)
logger = logging.getLogger(__name__)

def error(update, context):
    #Log Errors caused by Updates.
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # pp = PicklePersistence(filename = "bot_data")
    updater = Updater("1054268461:AAFSMepDnv3L4bq7bs9_ykhrnZVt24whpHU",use_context=True)

    dp = updater.dispatcher
    
    # Start Handler and help
    dp.add_handler(CommandHandler("start", Start))
    dp.add_handler(CommandHandler("Help", Help))

    # Add Handlers
    addPreOrderHandlersTo(dp)
    addOrderHandlersTo(dp)
    dp.add_handler(CommandHandler('Store', StoreMode))
    
    # Error Handler
    dp.add_error_handler(error)

    # Initialize bot_data
    for r in menu.rests():
        dp.bot_data[r] = {
            'Store Open': False,
            'orders': Queue(maxsize = 10)
        }

    # start checking for updates
    updater.start_polling()

    updater.idle()

def Start(update, context):
    #Prompt user to startJio
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Hi, weclome to SupperTogether! To start inviting, just /LetsMakan")

def Help(update,context):
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Cow goes Moo, cat goes meow, dogs go___?")

if __name__ == '__main__':
    main()