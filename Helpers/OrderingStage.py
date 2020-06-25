from openpyxl import load_workbook, workbook
from Helpers.Helper import InlineKeyboard
from Helpers.ExcelBuilder import Menu
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

sub_1, sub_2, sub_3 = range(3)

class order:
    def __init__(self, user, restaurant = None, address = None, phone = None):
        self.user = user
        self.restaurant = restaurant
        self.menu = Menu( "Menu.xlsx", restaurant)
        self.address = address
        self.phone = phone
        self.food = {}

    def addOrder(self, update, context):
        #Access Menu
        order_list = self.menu.list()

        # Create reply_markup.
        reply_markup = InlineKeyboard(order_list)
        
        # Header: Prompt user to select food/drink.
        context.bot.sendMessage(chat_id = update.effective_user.id,
                                    text = "Please select your food/drink:", reply_markup = reply_markup)

        return sub_1

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
            self.updateList(customer, item)
            
            return ConversationHandler.END

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
    
    def viewOrder(self, update, context):
        output = ""
        for customer in self.food :
            temp = self.food[customer]
            for item in temp :
                output = output + customer.first_name + " " + customer.last_name + " " + item + " x" + str(temp[item]) + "\n"
        context.bot.sendMessage(chat_id = update.effective_chat.id, text = output)

    def removeOrder(self, update, context):
        #step 1: List items chosen
        list_of_items = self.food[update.effective_user]
        
        #step 2: choose from menu
        if list_of_items is None:
            context.bot.sendMessage(chat_id = update.effective_user.id, text = "You have not ordered anything yet")
            
            return ConversationHandler.END
        
        else:
            # Create and send menu
            reply_markup = InlineKeyboard(list_of_items)
            context.bot.sendMessage(chat_id  = update.effective_user.id, text = "Select which item to delete", reply_markup = reply_markup)

            return sub_1
        
    def removeOrder_Helper(self, update, context):
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
            
            return ConversationHandler.END
    
    def build_handlers(self, dispatcher):
        order_conv_handler = ConversationHandler(entry_points = [CommandHandler("AddOrder", self.addOrder)], states = {
            sub_1 : [CallbackQueryHandler(self.addOrder_helper)]
        }, fallbacks = [CommandHandler("AddOrder", self.addOrder)], per_user = True, per_chat = False)

        remove_conv_handler = ConversationHandler(entry_points = [CommandHandler("RemoveOrder", self.removeOrder)], states = {
            sub_1 : [CallbackQueryHandler(self.removeOrder_Helper)]
        }, fallbacks = [CommandHandler("RemoveOrder", self.removeOrder)], per_user = True, per_chat = False)

        viewOrder_handler = CommandHandler("vieworder", self.viewOrder)

        dispatcher.add_handler(order_conv_handler)
        dispatcher.add_handler(remove_conv_handler)
        dispatcher.add_handler(viewOrder_handler)
