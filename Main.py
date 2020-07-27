# import
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
    TOKEN = open("TOKEN.txt", "r").read()

    # pp = PicklePersistence(filename = "bot_data")
    try:
        updater = Updater(token = TOKEN, use_context=True)
        updater.start_polling()
    except:
        print("Please input a valid token. To edit your token, open TOKEN.txt")
        return

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

    # Add test handlers
    test = ConversationHandler(entry_points = [CommandHandler("testStore", registerStore)], states = {
        1 : [CallbackQueryHandler(registerhelper)]
    }, fallbacks = [CommandHandler("testStore", registerStore)], per_chat = False)
    dp.add_handler(test)
    
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

    dp.bot_data["poll"] = {}
    # start checking for updates

    print("Finished processing")


    updater.idle()

def Start(update, context):
    #Prompt user to startJio
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Hi, welcome to SupperTogether! To start inviting, just /LetsMakan")

def Help(update,context):
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Welcome to SupperTogether!\n\nTo start ordering supper as a group, add me to your telegram group and /LetsMakan.\n\nVote for your favourite restaurant as a group using our Poll feature and choose your order from the restaurant chosen using /addOrder.\n\nRemember to click /endMakan after everyone is done ordering. Sit back and wait for your supper to be delivered, bon appetit!")

def StoreHelp(update,context):
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Welcome to SupperTogether!\n\nTo start receiving orders, remember to click /open to open your Store.\n\nYou will be notified whenever a customer makes an order.\n\nIf you feel like you're stuck at any point in time, simply click /menu to access the Main Menu.\n\nAt the end of the day, remember to close your Store via the Main Menu to stop receiving orders. Happy Cooking!")

def registerStore(update, context):

    list_of_rests = menu.rests()
    buttons = [[InlineKeyboardButton(list_of_rests[i], callback_data = i)] for i in range(len(list_of_rests))]
    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Please select a dummy store for testing:", reply_markup = reply_markup)

    return 1

def registerhelper(update, context):

    update.callback_query.answer()
    answer = update.callback_query.data
    user_id = update.effective_user.id

    r = stores.changeID(int(answer), user_id)
    print(r)

    #update stores
    for id in stores.toList("ID"):
        context.bot_data[id] = {
            'Store Open': False,
            'orders': Manager().list()
        }
    
    update.effective_message.edit_text(text = "{} ID has been swapped to your! Please do not register for more than 1 store, otherwise u will crash the bot :(".format(r), 
    reply_markup = None)



if __name__ == '__main__':
    main()