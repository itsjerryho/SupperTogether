from openpyxl import load_workbook, workbook
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

class order:
    def __init__(self, user, restuarant = None, address = None, phone = None):
        self.user = user
        self.restuarant = restuarant
        self.address = address
        self.phone = phone
        self.food = {}

    def addOrder(self, update, context):
        #Access Menu
        order_list = self.rest_menu()

        # Create and send menu.
        # Header: Prompt user to select food/drink.
        reply_markup = self.InlineKeyboard(order_list)
        context.bot.sendMessage(chat_id = update.effective_user.id,
                                    text = "Please select your food/drink:", reply_markup = reply_markup)

        #handle answer using addOrder_helper
        answer_handler = CallbackQueryHandler(lambda update, context: addOrder_helper(update, context))
        context.dispatcher.add_handler(addOrder_helper)

    def addOrder_helper(self, update, context):
        #check for if person has answered
        if(context.bot.answer_callback_query(update.callback_query.id)):
        
            #remove message text
            context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)
            
            #send new message
            item = update.callback_query.data
            context.bot.sendMessage(chat_id = update.effective_user.id,
                                    text = "You have ordered " + item)

            #save order
            customer = update.effective_user
            updateList(customer, item)

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
            self.food[name] = {customer:1}
    
    def viewOrder(self, update, context):
        output = ""
        for customer in self.food :
            temp = self.food[customer]
            for item in temp :
                output = output + customer.first_name + " " + customer.last_name + " " + item + " x" + temp[item] + "\n"
        context.bot.sendMessage(chat_id = update.effective_chat.id, text = output)

    def deleteOrder(self, update, context):
        #step 1: List items chosen
        list_of_items = self.food[update.effective_user]
        
        #step 2: choose from menu
        if list_of_items is None:
            context.bot.sendMessage(chat_id = update.effective_user.id, text = "You have not ordered anything yet")
        else:
            # Create and send menu
            reply_markup = self.InlineKeyboard(list_of_items)
            context.bot.sendMessage(chat_id  = update.effect_user.id, text = "Select which item to delete", reply_markup = reply_markup)
        
        #step 3: delete item
            deleteHelper_handler = CallbackQueryHandler(lambda update, context: deleteHelper(self, update, context))
            
            context.dispatcher.add_handler(deleteHelper_handler)

    def deleteHelper(self, update, context):
        if(context.bot.answer_callback_query(update.callback_query.id)):
            #remove message text
            context.bot.deleteMessage(update.effective_chat.id, update.callback_query.message.message_id)

            #delete order
            item = update.callback_query.data
            user = update.effective_user
            self.food[user][item]  = self.food[user][item] - 1
            if self.food[user][item] == 0:
                del self.food[user][item]
            if not bool(self.food[user]):
                del self.food[user]
            
            #send new message
            context.bot.sendMessage(chat_id = update.effective_user.id,
                                text = item + " has been deleted!" )

    def build_menu(self, buttons,
               n_cols,	
               header_buttons = None,
               footer_buttons = None):
	menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	if header_buttons:
		menu.insert(0, [header_buttons])
	if footer_buttons:
		menu.append([footer_buttons])
	return menu

    def InlineKeyboard(self, list_of_options):
        keyboard = [InlineKeyboardButton(item[1], callback_data = item[1]) for item in list_of_options]
        return InlineKeyboardMarkup(build_menu(keyboard, n_cols = 1))

    def rest_menu(self):
        #Menu
        Menu_wb = load_workbook(filename = 'Menu.xlsx')
        restaurant_ws = Menu_wb ['RESTAURANT A']
        ORDERID = restaurant_ws['A']
        ITEMNAME = restaurant_ws['B']

        #return list of orders[ORDERID, ITEMNAME]
        return [ [ORDERID[i].value, ITEMNAME[i].value] for i in range(0, len(ORDERID)) ]
        

