from openpyxl import load_workbook, workbook
from Helpers.Data import menu
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

sub_1, sub_2, sub_3 = range(3)

class Order:
    def __init__(self, user, restaurant = None, address = None, phone = None):
        self.user = user
        self.restaurant = restaurant
        self.address = address
        self.phone = phone
        self.food = {}

    def updateList(self, customer, item):
        #check if name exists
        if customer in self.food:
            temp = self.food[customer]
            #check if item exists
            if item in temp:
                temp[item] = temp[item] + 1
            else:
                temp[item] = 1
        else:
            self.food[customer] = {item:1}
    
    def removefood(self, customer, item):
        #delete order
        self.food[customer][item]  = self.food[customer][item] - 1
        if self.food[customer][item] == 0:
            del self.food[customer][item]
        if not bool(self.food[customer]):
            del self.food[customer]

    def __str__(self):
        username = self.user.first_name
        orders = ""
        for customer in self.food :
            temp = self.food[customer]
            for item in temp :
                orders = orders + customer.first_name + " " + item + " x" + str(temp[item]) + "\n"
        return (
            "User: " + username + "\n" + 
            "List of orders:\n" + orders + 
            "Phone: " + str(self.phone) + "\n"
            "Address: " + str(self.address)
        )
    
def addOrderHandlersTo(dispatcher):
    order_conv_handler = ConversationHandler(entry_points = [CommandHandler("AddOrder", addOrder)], states = {
        sub_1 : [CallbackQueryHandler(addOrder_helper)]
    }, fallbacks = [CommandHandler("AddOrder", addOrder)], per_user = True, per_chat = False)

    remove_conv_handler = ConversationHandler(entry_points = [CommandHandler("RemoveOrder", removeOrder)], states = {
        sub_1 : [CallbackQueryHandler(removeOrder_Helper)]
    }, fallbacks = [CommandHandler("RemoveOrder", removeOrder)], per_user = True, per_chat = False)

    viewOrder_handler = CommandHandler("vieworder", viewOrder)

    dispatcher.add_handler(order_conv_handler)
    dispatcher.add_handler(remove_conv_handler)
    dispatcher.add_handler(viewOrder_handler)


def addOrder(update, context):
    # Send Error
    if(messageError(update,context)):
        return ConversationHandler.END

    #Save chatID
    chat_id = update.effective_chat.id
    context.user_data["chat_id"] = chat_id

    # Retrieve information
    order = context.bot_data[chat_id]
    restaurant = order.restaurant
    
    #Access Menu
    ID_list = menu.listing(restaurant, data=0)
    Item_list = menu.listing(restaurant, data =1)
    Price_list = menu.listing(restaurant, data =2)

    #List of buttons
    buttons = [[InlineKeyboardButton(Item_list[i] + " - $" + "{:.2f}".format(Price_list[i]), callback_data= ID_list[i])] for i in range(len(ID_list))]

    # Create reply_markup.
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Header: Prompt user to select food/drink.
    context.bot.sendMessage(chat_id = update.effective_user.id,
                                text = "Please select your food/drink:", reply_markup = reply_markup)

    return sub_1

def addOrder_helper(update, context):
    query = update.callback_query
    query.answer()
    
    chat_id = context.user_data["chat_id"]
    context.user_data.clear()
    order = context.bot_data[chat_id]
    restaurant = order.restaurant

    # Answer
    answer = query.data

    #remove message text
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)
    
    #send new message
    item = menu.item(restaurant, answer)
    amount = menu.cost(restaurant, answer)
    context.bot.sendMessage(chat_id = update.effective_user.id,
                            text = "You have ordered " + item + 
                            "\nAmount: $" + "{:.2f}".format(amount))

    #save order
    customer = update.effective_user
    order.updateList(customer, answer)
    
    return ConversationHandler.END

def viewOrder(update, context):
    # Send Error
    if(messageError(update,context)):
        return ConversationHandler.END
    
    # Check chat_id
    chat_id = update.effective_chat.id
    food = context.bot_data[chat_id].food
    restaurant = context.bot_data[chat_id].restaurant

    # Check dictionary
    output = ""
    total = 0
    for customer in food :
        temp = food[customer]
        for id in temp :
            output = output + customer.first_name + " " + menu.item(restaurant, id) + " x" + "{:d}".format(temp[id]) + "\n"
            total = total + menu.cost(restaurant, id) * temp[id]
    context.bot.sendMessage(chat_id = update.effective_chat.id, text = output + "\nTotal: $" + "{:.2f}".format(total))

def removeOrder(update, context):
    # Send Error
    if(messageError(update,context)):
        return ConversationHandler.END
    
    # Check chat_id
    chat_id = update.effective_chat.id
    context.user_data["chat_id"] = chat_id
    order = context.bot_data[chat_id]
    food = order.food

    #step 1: List items chosen
    list_of_items = list(food[update.effective_user].keys())
    restaurant = order.restaurant
    
    #step 2: choose from menu
    if list_of_items is None:
        context.bot.sendMessage(chat_id = update.effective_user.id, text = "You have not ordered anything yet")
        
        return ConversationHandler.END
    
    else:
        # Create and send menu
        buttons = [[InlineKeyboardButton(menu.item(restaurant, id), callback_data= id)] for id in list_of_items]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.sendMessage(chat_id  = update.effective_user.id, text = "Select which item to delete", reply_markup = reply_markup)

        return sub_1
    
def removeOrder_Helper(update, context):
    # Check chat_id
    chat_id = context.user_data["chat_id"]
    context.user_data.clear()

    # Retrieve order and answers
    order = context.bot_data[chat_id] 
    user = update.effective_user
    restaurant = order.restaurant
    id = update.callback_query.data
    answer = menu.item(restaurant, id)

    # remove message text
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)
    
    #send new message
    context.bot.sendMessage(chat_id = update.effective_user.id,
                        text = answer + " has been deleted!" )
    
    
    order.removefood(user, id)
    
    return ConversationHandler.END

def messageError(update,context, chat_type = "group"):
    # Check where the message is coming from
    error = update.effective_message.chat.type != chat_type
    if(error):
        context.bot.sendMessage(update.effective_user.id, text = "Please send your commands in a group!")
    return error