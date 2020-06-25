from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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