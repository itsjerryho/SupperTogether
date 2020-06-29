from Helpers.OrderingStage import Order
from Helpers.Data import menu, stores
from openpyxl import load_workbook, workbook
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

sub_1, sub_2, sub_3, sub_4 = range(4)

def LetsMakan (update, context):
    # Check where the message is coming from
    if (update.effective_message.chat.type != "group"):
        context.bot.sendMessage(update.effective_user.id, text = "Send your commands in a group")
        return ConversationHandler.END

    context.user_data["chat_id"] = update.effective_chat.id
    # prompt user to choose a restaurant
    list_of_restaurants = menu.rests()
    buttons = [[InlineKeyboardButton(r, callback_data=r)] for r in list_of_restaurants]
    reply_markup = InlineKeyboardMarkup(buttons)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Please select a restaurant: ", reply_markup = reply_markup)

    # Add user to botdata
    # Create order object
    new_order = Order(update.effective_user)
    context.bot_data[context.user_data["chat_id"]] = new_order

    return sub_1

def Phone(update, context):
    restaurant  = update.callback_query.data
    context.bot_data[context.user_data["chat_id"]].restaurant = restaurant
    context.bot.editMessageReplyMarkup(chat_id = update.effective_user.id, message_id = update.callback_query.message.message_id, reply_markup = None)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Please key in your phone number: ")
    
    return sub_2

def address(update, context):
    phoneNumber = update.effective_message.text
    context.bot_data[context.user_data["chat_id"]].phone = phoneNumber
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Please key in your address details: ")
    
    return sub_3

def LetsMakanEnd(update, context):
    # save results
    order = context.bot_data[context.user_data["chat_id"]] 
    order.address = update.effective_message.text

    # Prompt user to start ordering!
    context.bot.sendMessage(chat_id = context.user_data["chat_id"], text = 
        order.restaurant + " is chosen! Use the following commands: " + 
        "\n/addOrder - add order" + 
        "\n/viewOrder - view all orders" + 
        "\n/removeOrder - remove an order" +
        "\n/EndMakan - EndMakan")

    return ConversationHandler.END

def EndMakan(update, context):
    # Accept only commands from group chat
    if (update.effective_message.chat.type != "group"):
        context.bot.sendMessage(update.effective_user.id, text = "Send your commands in a group")
        return ConversationHandler.END

    # Only Host can close Makan
    if context.bot_data[update.effective_chat.id].user.id != update.effective_user.id:
        # End Convo
        context.bot.sendMessage(chat_id = update.effective_chat.id, text = "Only Host can end Makan")
        return ConversationHandler.END

    # Save result
    order = context.bot_data[update.effective_chat.id]
    context.bot_data[stores.ID(order.restaurant)]['orders'].put(order)

    # Prompt store order incoming
    context.bot.sendMessage(chat_id = stores.ID(order.restaurant), text = "You have just received an order!\nClick View Order to view.")

    # Clear bot data and user cache
    del context.bot_data[update.effective_chat.id]
    context.user_data.clear()

def Cancel(update, context):
    # Ends conversation right away
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = "See you next time!")

    context.user_data.clear()
    return ConversationHandler.END

def addPreOrderHandlersTo(dispatcher):
    # Build handlers
    start_conv = ConversationHandler(entry_points = [CommandHandler("LetsMakan", LetsMakan)], states = {
        sub_1 : [CallbackQueryHandler(Phone)],
        sub_2 : [MessageHandler(Filters.text, address)],
        sub_3 : [MessageHandler(Filters.text, LetsMakanEnd)]
    }, fallbacks = [CommandHandler("cancel", Cancel)], per_user = True, per_chat= False)
    
    # Add to dispatcher
    dispatcher.add_handler(start_conv)
    dispatcher.add_handler(CommandHandler("EndMakan", EndMakan))