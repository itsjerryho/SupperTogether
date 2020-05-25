from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def main():
    updater = Updater("1054268461:AAFSMepDnv3L4bq7bs9_ykhrnZVt24whpHU", use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler(“StartJio”, StartJio)
	dp.add_handler(CommandHandler(“Store”, StoreMode)
	dp.add_handler(CommandHandler(“AddOrder”, OrderingStage.AddOrder)
    dp.add_handler(CommandHandler(“ViewOrder”, OrderingStage.ViewOrder)
    dp.add_handler(CommandHandler(“RemoveOrder”, OrderingStage.RemoveOrder)
    dp.add_handler(CommandHandler(“CloseJio”, OrderingStage.CloseJio)
    # dp.add_handler(CommandHandler(“Help”, help)

    # start checking for updates
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()