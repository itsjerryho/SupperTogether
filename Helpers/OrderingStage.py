from openpyxl import load_workbook, workbook
from Helpers.Data import menu
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

sub_1, sub_2, sub_3 = range(3)
option_1, option_2, final = range(3)

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
        option_1 : [CallbackQueryHandler(lambda update, context: options(update, context, option_1))],
        option_2 : [CallbackQueryHandler(lambda update, context: options(update, context, option_2))],
        final : [CallbackQueryHandler(lambda update, context: addOrder_helper(update, context, final))]
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

    # Cache answers inside user_data["order"]
    context.user_data["order"] = [None]*3
    
    # Header: Prompt user to select food/drink.
    context.bot.sendMessage(chat_id = update.effective_user.id,
                                text = "Please select your food/drink:", reply_markup = reply_markup)

    return option_1

def options(update, context, option):
    # Retrieve answer
    query = update.callback_query
    data = query.data

    # Save answer
    context.user_data["order"][option] = data

    # Obtain ID
    ID = context.user_data["order"][0]

    # Ask next option
    order = context.bot_data[context.user_data["chat_id"]]
    list_of_choices = menu.item(order.restaurant, ID , option + 1)
    list_of_costs = menu.cost(order.restaurant, ID, option + 1)

    # Check if next option exists
    if list_of_choices is None:
        return addOrder_helper(update, context, option)

    # Build reply_markup
    buttons = ([[InlineKeyboardButton(list_of_choices[i] + " - $" + "{:.2f}".format(list_of_costs[i]), callback_data=i)] for i in range(len(list_of_choices))])
    reply_markup = InlineKeyboardMarkup(buttons)

    # Edit message
    update.effective_message.edit_text(text = "Please select an option: ",reply_markup = reply_markup)

    return option + 1

def addOrder_helper(update, context, option):
    query = update.callback_query
    query.answer()
    
    chat_id = context.user_data["chat_id"]
    order = context.bot_data[chat_id]
    restaurant = order.restaurant

    # save answer
    answer = query.data
    context.user_data["order"][option] = answer

    #remove message text
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)
    
    #send new message
    item = menu.item(restaurant, tuple(context.user_data["order"]))
    amount = menu.cost(restaurant, tuple(context.user_data["order"]))
    context.bot.sendMessage(chat_id = update.effective_user.id,
                            text = "You have ordered " + item + 
                            "\nAmount: $" + "{:.2f}".format(amount))

    #save order
    customer = update.effective_user
    order.updateList(customer, tuple(context.user_data["order"]))

    # Clear cache
    context.user_data.clear()
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
    
    #step 1: check if user has ordered anything
    if update.effective_user not in food:
        context.bot.sendMessage(chat_id = update.effective_user.id, text = "You have not ordered anything yet")
        
        return ConversationHandler.END
    
    else:        
        #step 2: List items chosen
        list_of_items = food[update.effective_user].keys()
        
        # Create and send menu
        restaurant = order.restaurant
        context.user_data["orders"] = list(list_of_items)
        buttons = [[InlineKeyboardButton(menu.item(restaurant, context.user_data["orders"][i]), callback_data= i)] for i in range(len(context.user_data["orders"]))]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.sendMessage(chat_id  = update.effective_user.id, text = "Select which item to delete", reply_markup = reply_markup)

        return sub_1
    
def removeOrder_Helper(update, context):
    # Check chat_id
    chat_id = context.user_data["chat_id"]

    # Retrieve order and answers
    order = context.bot_data[chat_id] 
    user = update.effective_user
    restaurant = order.restaurant
    i = int(update.callback_query.data)
    answer = menu.item(restaurant, context.user_data["orders"][i])

    # remove message text
    context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)
    
    #send new message
    context.bot.sendMessage(chat_id = update.effective_user.id,
                        text = answer + " has been deleted!" )
    
    
    order.removefood(user, context.user_data["orders"][i])

    #clear user data
    context.user_data.clear()
    
    return ConversationHandler.END

def messageError(update,context, chat_type = "group"):
    # Check where the message is coming from
    error = update.effective_message.chat.type != chat_type
    if(error):
        context.bot.sendMessage(update.effective_user.id, text = "Please send your commands in a group!")
    return error