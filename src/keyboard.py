from telebot import types

def create_custom_keyboard(include_main_menu=False):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    if include_main_menu:
        main_menu_button = types.KeyboardButton("Main Menu ")
        keyboard.add(main_menu_button)
    else:
        button1 = types.KeyboardButton("Витрати")
        button2 = types.KeyboardButton("Button 2")
        button3 = types.KeyboardButton("Button 3")
        button4 = types.KeyboardButton("Settings ⚙️")
        keyboard.add(button1, button2, button3, button4)
    
    return keyboard
