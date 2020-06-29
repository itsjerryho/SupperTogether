from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, CallbackContext, PicklePersistence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from multiprocessing import Queue
from Helpers.Data import menu
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


def closeStore(update, context):
    bot_data = context.bot_data
    print("Printing in CloseStore!!!!")
    print(bot_data)
    bot_data["Ah Beng Drink"]["Store Open"] = False
    print(bot_data)
    update.message.reply_text("You will stop receiving orders. Have a good rest!")
    return ConversationHandler.END

def openStore(update, context):
    
    bot_data = context.bot_data
    print("Printing in openStore!!!!")
    print(bot_data)
    # TODO: specify exactly which store is it in bot_data using update.user.id (store's own id)
    bot_data["Ah Beng Drink"]["Store Open"] = True
    print(bot_data)
    reply_keyboard = [['Close Shop'],
                  ['View Orders']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("You will start receiving orders. \n We will notify you when there's a new order.", reply_markup = markup)

    return CHOOSING


def accepting(update, context):
        print("inside Accepting!")
        customer_name_of_orderChosen = update.callback_query.data.split("accept_")[1]
        print("Customer Name: {}".format(customer_name_of_orderChosen))
        keyboard = [[InlineKeyboardButton("30 mins", callback_data = "30 mins_{}".format(customer_name_of_orderChosen))],
        [InlineKeyboardButton("1 hour", callback_data = "1 hour_{}".format(customer_name_of_orderChosen))],
        [InlineKeyboardButton("1.5 hours", callback_data = "1.5 hours_{}".format(customer_name_of_orderChosen))],
        [InlineKeyboardButton("2 hours", callback_data = "2 hours_{}".format(customer_name_of_orderChosen))],
        [InlineKeyboardButton("Back", callback_data="Back_{}".format(customer_name_of_orderChosen))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.sendMessage(chat_id = update.effective_user.id, text = "Estimated Waiting Time: ", reply_markup = reply_markup)

        return CHOOSING_WAITINGTIME

def rejecting(update, context):
    customer_name_of_orderChosen = update.callback_query.data.split("reject_")[1]
    keyboard = [[InlineKeyboardButton("Reject", callback_data = "Reject_{}".format(customer_name_of_orderChosen))],
    [InlineKeyboardButton("Back", callback_data="Back_{}".format(customer_name_of_orderChosen))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Do you really want to reject this order?", reply_markup = reply_markup)
    return REJECTING

def rejected(update, context):
    customer_name_of_orderChosen = update.callback_query.data.split("Reject_")[1]
    user_data = context.user_data
    user_data["CustomerName"] = customer_name_of_orderChosen
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "You have rejected the order. Please input your reason for rejection this order. (ie. Out of stock, no time etc)")
    return POST_REJECTION

def send_rejection(update, context):
    customer_name_of_orderChosen = context.user_data["CustomerName"]
    reason = update.message.text
    customerID = ""
    # orders is a queue of Order objects
    orders = context.bot_data["Ah Beng Drink"]["orders"]
    # orders is a queue of Order objects
    # making this queue into a list
    orderList = []
    tempQueue = Queue(maxsize= 10)
    while orders.qsize() != 0:
        order = orders.get()
        orderList.append(order)
        tempQueue.put(order)

    # assign tempQueue as the queue in orders so the data will not be lost
    context.bot_data["Ah Beng Drink"]["orders"] = tempQueue

    for order in orderList:
        if order.user.first_name == customer_name_of_orderChosen:
            customerID = order.user.id

    print("Customer UserID: {}".format(customerID))
    # send Message to customer
    context.bot.sendMessage(chat_id = customerID, text = "Sorry, your order has been rejected. Reason: {}".format(reason))
    context.user_data.pop("CustomerName", None) 
    reply_keyboard = [['Done']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("We will inform the customer that their order has been rejected. Have a nice day!", reply_markup = markup)
    return COMPLETED

def accepted(update, context):
    timeChosen = update.callback_query.data.split("_")[0]
    customerName = update.callback_query.data.split("_")[1]
    print('in Accepted!')
    customerID = ""
    orders = context.bot_data["Ah Beng Drink"]["orders"]
    # orders is a queue of Order objects
    # making this queue into a list
    orderList = []
    tempQueue = Queue(maxsize= 10)
    while orders.qsize() != 0:
        order = orders.get()
        orderList.append(order)
        tempQueue.put(order)

    for order in orderList:
        if order.user.first_name == customerName:
            customerID = order.user.id
    
    
    print('customerID: {}'.format(customerID))

    # assign tempQueue as the queue in orders so the data in Queue will not be lost
    context.bot_data["Ah Beng Drink"]["orders"] = tempQueue

    context.bot.sendMessage(chat_id = customerID, text = "Your order has been accepted! Estimated Waiting Time: {}".format(timeChosen))

    reply_keyboard = [['Done']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    context.bot.sendMessage(chat_id = update.effective_user.id, reply_markup = markup, text ="You have selected {} as the estimated waiting time. We will update the customer. Happy Cooking!".format(timeChosen))

    return COMPLETED

def view_orders(update, context):
    bot_data = context.bot_data
    #TODO: Replace StoreA with storeID
    storeA = bot_data["Ah Beng Drink"]
    print(storeA)
    orders = bot_data["Ah Beng Drink"]["orders"]
    # orders is a queue of Order objects
    # making this queue into a list of Order objects
    orderList = []
    tempQueue = Queue(maxsize= 10)
    while orders.qsize() != 0:
        order = orders.get()
        orderList.append(order)
        tempQueue.put(order)

    # assign tempQueue as the queue in orders so the data will not be lost
    bot_data["Ah Beng Drink"]["orders"] = tempQueue

    # create another list that contains just the customerName for the sake of 
    # creating the keyboard
    newList = []
    for x in orderList:
        newList.append(x.user.first_name)
    # generate menu based on Customer Name
    markup = InlineKeyboard(newList)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Choose an order:", reply_markup = markup)
    return VIEWING_SPECIFIC_ORDER

def specific_order(update, context):
    query = update.callback_query.data
    # account for special case where Back is used
    if "Back" in query:
        query = query.split("Back_")[1]
    customer_name_of_orderChosen = query
    print("Inside Specific_Order")
    print("Customer Name: {}".format(customer_name_of_orderChosen))
    # TODO: Render keys based on order status
    keyboard = [[InlineKeyboardButton("Items Ordered", callback_data = "view_{}".format(customer_name_of_orderChosen))],
            [InlineKeyboardButton("Accept Order", callback_data = "accept_{}".format(customer_name_of_orderChosen))],
            [InlineKeyboardButton("Reject Order", callback_data = "reject_{}".format(customer_name_of_orderChosen))],
            [InlineKeyboardButton("Back", callback_data = "back")]
            ]
    new_reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = "Choose an Action", reply_markup = new_reply_markup)
    return AFTER_VIEWING_ORDER

def list_order(update, context):
    # get back the original string name without the "view" word
    customer_name_of_orderChosen = update.callback_query.data.split("view_")[1]
    print("in List Order!")
    print('customer Name: {}'.format(customer_name_of_orderChosen))
    # find the order
    orderDict = {}
    orders = context.bot_data["Ah Beng Drink"]["orders"]
    # orders is a queue of Order objects
    # making this queue into a list
    orderList = []
    tempQueue = Queue(maxsize= 10)
    while orders.qsize() != 0:
        order = orders.get()
        orderList.append(order)
        tempQueue.put(order)

    # assign tempQueue as the queue in orders so the data will not be lost
    context.bot_data["Ah Beng Drink"]["orders"] = tempQueue

    for order in orderList:
        if order.user.first_name == customer_name_of_orderChosen:
            orderDict = order.food

    # create another dictionary with just the item id and quantity
    newDict = {}
    for userOrders in orderDict.values():
        for foodID, quantity in userOrders.items():
            # check if foodID exist in newDict.
            # if exist, increment the count
            # if doesn't exist, add in the foodID with qty = 1
            if foodID in newDict:
                oldValue = newDict[foodID]
                newDict[foodID] = oldValue + quantity
            else:
                newDict[foodID] = 1
    
    textForm = "Items Ordered \n"
    # convert dict into text
    for foodID, quantity in newDict.items():
        textForm += menu.item('Ah Beng Drink', foodID) + ": {}".format(quantity) + "\n"

    # Create Back button
    keyboard = [[InlineKeyboardButton("Back", callback_data=customer_name_of_orderChosen)]]
    new_reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.sendMessage(chat_id = update.effective_user.id, text = textForm, reply_markup = new_reply_markup)
    return VIEWING_SPECIFIC_ORDER


def addShopHandlersTo(dispatcher):
    # Build handlers
    order_handler = ConversationHandler(
        entry_points=[CommandHandler('open', openStore)],
        
        states={
            CHOOSING: [MessageHandler(Filters.regex('^Close Shop$'),
                                      closeStore),
                       MessageHandler(Filters.regex('^View Orders$'),
                                      view_orders)
                       ],
            VIEWING_SPECIFIC_ORDER: [CallbackQueryHandler(specific_order)],
            AFTER_VIEWING_ORDER: [CallbackQueryHandler(list_order, pattern="view"),
             CallbackQueryHandler(accepting, pattern="accept"),
             CallbackQueryHandler(rejecting, pattern="reject"),
             CallbackQueryHandler(view_orders, pattern="back")
            ],
            CHOOSING_WAITINGTIME:[CallbackQueryHandler(specific_order, pattern="Back"), 
            CallbackQueryHandler(accepted)],
            REJECTING:[CallbackQueryHandler(specific_order, pattern="Back"), 
            CallbackQueryHandler(rejected)],
            POST_REJECTION:[MessageHandler(Filters.text, send_rejection)],
            COMPLETED:[MessageHandler(Filters.regex('^Done$'), openStore)]
        },

        fallbacks = [CommandHandler('default', openStore)]
    )
    
    
    # Add to dispatcher
    dispatcher.add_handler(order_handler)
