from Helpers.OrderingStage import order
from openpyxl import load_workbook, workbook
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

Master_list_of_jios = {}

def StartJio (update, context):
    # prompt user to choose a restaurant
    list_of_restaurants = ["Restaurant A", "Restaurant B"]
    reply_markup = InlineKeyboard(list_of_restaurants)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Please select a restaurant: ", reply_markup = reply_markup)

    # User a handler to handle answer
    StartJio_handler = CallbackQueryHandler = (StartJio_helper)
    context.dispatcher.add_handler(StartJio_handler)

def StartJio_helper(update, context):
    # save results
    restaurant  = update.callback_query.data

    # remove message
    context.bot.deleteMessage(update.effective_user.id, update.callback_query.message.messageid)

    # Move on to start ordering.

    # Create order object
    new_order = order(update.effective_user, restaurant)
    Master_list_of_jios[update.effective_user: new_order]

    # add lower level handlers to the context
    context.dispatcher.add_handler(CommandHandler("AddOrder", order.addOrder))
    context.dispatcher.add_handler(CommandHandler("ViewOrder", order.viewOrder))
    context.dispatcher.add_handler(CommandHandler("RemoveOrder", order.deleteOrder))

def CloseJio(update, context):
    # Save all results
    closed_order = Master_list_of_jios[update.effective_user]
    print(closed_order)

def build_menu(buttons,
               n_cols,	
               header_buttons = None,
               footer_buttons = None):
	menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	if header_buttons:
		menu.insert(0, [header_buttons])
	if footer_buttons:
		menu.append([footer_buttons])
	return menu

def InlineKeyboard(list_of_options):
    keyboard = [InlineKeyboardButton(option, callback_data = option) for option in list_of_options]
    return InlineKeyboardMarkup(build_menu(keyboard, n_cols = 1))
