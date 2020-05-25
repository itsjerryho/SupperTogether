# import function name 
from Helpers import StartJio, StoreMode, AddOrder, ViewOrder, RemoveOrder, CloseJio

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def main():
    updater = Updater("1054268461:AAFSMepDnv3L4bq7bs9_ykhrnZVt24whpHU", use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(“StartJio”, StartJio)
	dp.add_handler(CommandHandler(“Store”, StoreMode)
	dp.add_handler(CommandHandler(“AddOrder”, AddOrder)
    dp.add_handler(CommandHandler(“ViewOrder”, ViewOrder)
    dp.add_handler(CommandHandler(“RemoveOrder”, RemoveOrder)
    dp.add_handler(CommandHandler(“CloseJio”, CloseJio)
    # dp.add_handler(CommandHandler(“Help”, help)

    # start checking for updates
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()