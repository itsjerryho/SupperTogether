from Helpers.OrderingStage import order
from openpyxl import load_workbook, workbook
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

Master_list_of_jios = {}

sub_1, sub_2 = range(2)

def StartJio (update, context):
    # prompt user to choose a restaurant
    list_of_restaurants = ["Restaurant A", "Restaurant B"]
    reply_markup = InlineKeyboard(list_of_restaurants)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Please select a restaurant: ", reply_markup = reply_markup)

    return sub_1

def StartJio_helper(update, context):
    # save results
    restaurant  = update.callback_query.data

    # remove message
    context.bot.deleteMessage(update.effective_user.id, update.callback_query.message.messageid)

    # Move on to start ordering.

    # Create order object
    new_order = order(update.effective_user, restaurant)
    Master_list_of_jios[update.effective_user] = new_order

    # add lower level handlers to the context
    new_order.build_handlers(context.dispatcher)

    # Prompt user to start ordering!
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = restaurant + " is chosen! Use the following commands: " + 
    "\n/addOrder - add order" + 
    "\n/viewOrder - view all orders" + 
    "\n/removeOrder - remove an order")

    return ConversationHandler.END

def CloseJio(update, context):
    # Save all results
    closed_order = Master_list_of_jios[update.effective_user]
    print(closed_order.food)

def Cancel(update, context):
    # Ends conversation right away
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "See you next time!")
    return ConversationHandler.END

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

start_conv = ConversationHandler(entry_points = [CommandHandler("startjio", StartJio)], states = {
    sub_1 : [CallbackQueryHandler(StartJio_helper)]
}, fallbacks = [CommandHandler("cancel", Cancel)], per_user = True, per_chat= False)