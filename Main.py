# import
from telegram.ext import Updater, CommandHandler
from Helpers.PreOrderingStage import start_conv, CloseJio
from Helpers.StoreInterface import StoreMode

import logging
#Loggin and errors
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level = logging.INFO)
logger = logging.getLogger(__name__)

def error(update, context):
    #Log Errors caused by Updates.
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater("1054268461:AAFSMepDnv3L4bq7bs9_ykhrnZVt24whpHU", use_context=True)

    dp = updater.dispatcher
    dp.add_handler(start_conv)
    dp.add_handler(CommandHandler('Store', StoreMode))
    dp.add_handler(CommandHandler('CloseJio', CloseJio))
    dp.add_error_handler(error)
    # dp.add_handler(CommandHandler(“Help”, help)

    # start checking for updates
    updater.start_polling()

    updater.idle()

def Start(update, context):
    #Prompt user to startJio
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Hi, weclome to SupperTogether! To start jio people, just /StartJio")

if __name__ == '__main__':
    main()