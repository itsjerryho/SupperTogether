from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext, PicklePersistence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from multiprocessing import Queue
from Helpers.Data import menu, stores
import logging

#Loggin
logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level = logging.INFO)

CHOOSING, VIEWING_SPECIFIC_ORDER, AFTER_VIEWING_ORDER, CHOOSING_WAITINGTIME, REJECTING, POST_REJECTION, COMPLETED = range(7)


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
    keyboard = [InlineKeyboardButton(item, callback_data = item) for item in list_of_options]
    return InlineKeyboardMarkup(build_menu(keyboard, n_cols = 1))

def defaultMenu(update, context):

    # clear chosen order data (if there's any)
    context.user_data.pop("order", None)

    # display the menu options 
    reply_keyboard = [['Close Shop'],
                  ['View Orders']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("Choose an action:", reply_markup = markup)

    return CHOOSING
     

def closeStore(update, context):
    # clear chosen order data (if there's any)
    context.user_data.pop("order", None)

    # TODO: Reject any remaining orders (if any)

    # TODO: Ask Merlin to prevent ordering stage from sending stallowners any messages 
    bot_data = context.bot_data
    storeID = update.effective_user.id
    bot_data[storeID]["Store Open"] = False
    update.message.reply_text("You will stop receiving orders. Have a good rest!")
    return ConversationHandler.END

def openStore(update, context):
    
    bot_data = context.bot_data
    storeID = update.effective_user.id

    if bot_data[storeID]["Store Open"]:
        update.message.reply_text("Your store is already open! Use /menu to access the main menu.")
        return ConversationHandler.END
    else:
        bot_data[storeID]["Store Open"] = True    
        bot_data[storeID]["Store Open"] = True
        reply_keyboard = [['Close Shop'],
                    ['View Orders']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text("You will start receiving orders. \n We will notify you when there's a new order.", reply_markup = markup)

        return CHOOSING


def accepting(update, context):
        # remove 'Choose an order'
        context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

        keyboard = ["30 mins", "1 hour", "1.5 hours", "2 hours", "Back"]
        reply_markup = InlineKeyboard(keyboard)
        context.bot.sendMessage(chat_id = update.effective_user.id, text = "Estimated Waiting Time: ", reply_markup = reply_markup)

        return CHOOSING_WAITINGTIME

def rejecting(update, context):
    # remove 'choose an action'
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

    keyboard = ["Reject", "Back"]

    reply_markup = InlineKeyboard(keyboard)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Do you really want to reject this order?", reply_markup = reply_markup)
    return REJECTING

def rejected(update, context):
    # remove 'do u really want to reject this order'
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

    context.bot.sendMessage(chat_id = update.effective_user.id, text = "You have rejected the order. Please input your reason for rejection this order. (ie. Out of stock, no time etc)")
    return POST_REJECTION

def send_rejection(update, context):

    reason = update.message.text
    customerID = context.user_data["order"].user.id

    # send Message to customer
    context.bot.sendMessage(chat_id = customerID, text = "Sorry, your order has been rejected. Reason: {}".format(reason))
    # context.user_data.pop("CustomerName", None) 
    reply_keyboard = [['Done']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("We will inform the customer that their order has been rejected. Have a nice day!", reply_markup = markup)
    return COMPLETED

def accepted(update, context):
    # remove' estimated waiting time'
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

    timeChosen = update.callback_query.data

    customerID = context.user_data["order"].user.id

    print('customerID: {}'.format(customerID))
    
    context.bot.sendMessage(chat_id = customerID, text = "Your order has been accepted! Estimated Waiting Time: {}".format(timeChosen))

    reply_keyboard = [['Done']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    context.bot.sendMessage(chat_id = update.effective_user.id, reply_markup = markup, text ="You have selected {} as the estimated waiting time. We will update the customer. Happy Cooking!".format(timeChosen))

    return COMPLETED

def view_orders(update, context):
    # remove 'Choose an Action'
    if hasattr(update.callback_query, 'message'): 
        context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

    bot_data = context.bot_data
    storeID = update.effective_user.id
    queue = bot_data[storeID]["orders"]

    # orders is a queue of Order objects
    # making this queue into a list of Order objects
    orderList = []
    tempQueue = Queue(maxsize= 10)
    while queue.qsize() != 0:
        order = queue.get()
        orderList.append(order)
        tempQueue.put(order)

    # assign tempQueue as the queue in orders so the data will not be lost
    bot_data[storeID]["orders"] = tempQueue

    # create another list that contains just the customerName for the sake of 
    # creating the keyboard
    newList = []
    for order in orderList:
        newList.append(order.user.first_name)
    
    # generate menu based on Customer Name
    markup = InlineKeyboard(newList)

    # TODO: Fix the bug where customers have the same first name. Perhaps add their unique id to the name
    # TODO: Add a back button
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Choose an order:", reply_markup = markup)
    return VIEWING_SPECIFIC_ORDER

def specific_order(update, context):
    query = update.callback_query.data

    # delete previous message
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

    if query != "Back":
        customerName = query
        # find and save order in user_data
        print("finding order in specific order")
        # find order based on Customer Name
        orderObj = None
        storeID = update.effective_user.id
        orders = context.bot_data[storeID]["orders"]
        # orders is a queue of Order objects
        # making this queue into a list
        orderList = []
        tempQueue = Queue(maxsize= 10)
        while orders.qsize() != 0:
            order = orders.get()
            orderList.append(order)
            tempQueue.put(order)

        # assign tempQueue as the queue in orders so the data will not be lost
        context.bot_data[storeID]["orders"] = tempQueue

        for order in orderList:
            if order.user.first_name == customerName:
                orderObj = order
        
        # save order object
        context.user_data["order"] = orderObj
    else:
        print("Back button was clicked, no need to update user_data")
    
    # TODO: Render keys based on order status
    keyboard = ["Items Ordered", "Accept Order", "Reject Order", "Back"]

    new_reply_markup = InlineKeyboard(keyboard)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Choose an Action", reply_markup = new_reply_markup)
    return AFTER_VIEWING_ORDER

def list_order(update, context):
    # remove previous message
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

    order = context.user_data["order"]

    storeID = update.effective_user.id

    orderFoodDict = order.food
    # create another dictionary with just the item id and quantity
    newDict = {}
    for userOrders in orderFoodDict.values():
        for foodID, quantity in userOrders.items():
            # check if foodID exist in newDict.
            # if exist, increment the count
            # if doesn't exist, add in the foodID with qty = 1
            if foodID in newDict:
                oldValue = newDict[foodID]
                newDict[foodID] = oldValue + quantity
            else:
                newDict[foodID] = 1
            
    textForm = "Address: \n{} \n\nContact: \n{} \n\n".format(order.address, order.phone)
    textForm += "Items Ordered \n"
    # convert dict into text
    for foodID, quantity in newDict.items():
        textForm += menu.item(stores.stores(storeID), foodID) + ": {}".format(quantity) + "\n"

    # Create Back button
    keyboard = [[InlineKeyboardButton("Back", callback_data="Back")]]
    new_reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = textForm, reply_markup = new_reply_markup)
    return VIEWING_SPECIFIC_ORDER


def addShopHandlersTo(dispatcher):
    # Build handlers
    order_handler = ConversationHandler(
        entry_points=[CommandHandler('open', openStore), CommandHandler('menu', defaultMenu)],
        
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Close Shop$'),
                                      closeStore),
                       MessageHandler(Filters.regex('^View Orders$'),
                                      view_orders)
                       ],
            VIEWING_SPECIFIC_ORDER: [CallbackQueryHandler(specific_order)],
            AFTER_VIEWING_ORDER: [CallbackQueryHandler(list_order, pattern="Items"),
             CallbackQueryHandler(accepting, pattern="Accept"),
             CallbackQueryHandler(rejecting, pattern="Reject"),
             CallbackQueryHandler(view_orders, pattern="Back")
            ],
            CHOOSING_WAITINGTIME:[CallbackQueryHandler(specific_order, pattern="Back"), 
            CallbackQueryHandler(accepted)],
            REJECTING:[CallbackQueryHandler(specific_order, pattern="Back"), 
            CallbackQueryHandler(rejected)],
            POST_REJECTION:[MessageHandler(Filters.text, send_rejection)],
            COMPLETED:[MessageHandler(Filters.regex('^Done$'), defaultMenu)]
        },

        fallbacks = [CommandHandler('menu', defaultMenu), CommandHandler('open', openStore)]
    )
    
    
    # Add to dispatcher
    dispatcher.add_handler(order_handler)
