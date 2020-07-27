# import
from telegram.ext import Updater, CommandHandler
from Helpers.PreOrderingStage import addPreOrderHandlersTo
from Helpers.OrderingStage import addOrderHandlersTo
from Helpers.StoreInterface import addShopHandlersTo
from Helpers.Data import menu, stores
from multiprocessing import Manager

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
    print("Adding Handlers...")
    dp.add_handler(CommandHandler("start", Start))
    dp.add_handler(CommandHandler("Help", Help))
    dp.add_handler(CommandHandler("StoreHelp", StoreHelp))


    # Add Handlers
    print("Adding More Handlers...")
    addPreOrderHandlersTo(dp)
    addOrderHandlersTo(dp)
    addShopHandlersTo(dp)
    
    # Error Handler
    dp.add_error_handler(error)

    # Print store data
    print(stores.df)
    
    print("Loading bot data...")
    # Initialize bot_data
    for id in stores.toList("ID"):
        dp.bot_data[id] = {
            'Store Open': False,
            'orders': Manager().list()
        }

    # start checking for updates

    print("Finished processing")
    updater.start_polling()

    updater.idle()

def Start(update, context):
    #Prompt user to startJio
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Hi, welcome to SupperTogether! To start inviting, just /LetsMakan")

def Help(update,context):
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Welcome to SupperTogether! \n To start ordering supper as a group, add me to your telegram group and /LetsMakan. \n Vote for your favourite restaurant as a group using our Poll feature and choose your order from the restaurant chosen using /addOrder. \n Remember to click /endMakan after everyone is done ordering. Sit back and wait for your supper to be delivered, bon appetit!")

def StoreHelp(update,context):
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Welcome to SupperTogether! \n To start receiving orders, remember to click /open to open your Store. \n You will be notified instantly once a customer makes an order. \n If you feel like you're stuck at any point in time, simply click /menu to access the Main Menu. \n At the end of the day, remember to close your Store via the Main Menu to stop receiving orders. Happy Cooking!")

if __name__ == '__main__':
    main()