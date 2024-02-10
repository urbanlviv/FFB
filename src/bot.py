import telebot
from config import TOKEN, whitelist, permission_denied_message
from telebot import types
import schedule
import threading
import logging
import time
import requests

bot = telebot.TeleBot(TOKEN)

users_notifications = {}

def get_latest_release_info():
    url = 'https://api.github.com/repos/urbanlviv/FFB/releases/latest'
    response = requests.get(url)
    if response.status_code == 200:
        release_info = response.json()
        version = release_info['tag_name']
        description = release_info['body']
        return version, description
    else:
        return None, None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_custom_keyboard():
    logger.info("Creating custom keyboard")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Витрати")
    button2 = types.KeyboardButton("Дохід")
    button3 = types.KeyboardButton("Бюджет")
    button4 = types.KeyboardButton("Статистика")
    button5 = types.KeyboardButton("Налаштування")
    button6 = types.KeyboardButton("/restart")
    keyboard.add(button1, button2, button3, button4, button5, button6)
    return keyboard

def send_menu_with_keyboard(chat_id):
    logger.info(f"Sending menu to chat_id {chat_id}")
    keyboard = create_custom_keyboard()
    bot.send_message(chat_id, "Оберіть опцію:", reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    logger.info("Received /start command")
    if message.from_user.id in whitelist:
        send_menu_with_keyboard(message.chat.id)
    else:
        bot.send_message(message.chat.id, permission_denied_message)

@bot.message_handler(commands=['restart'])
def restart(message):
    logger.info("Received /restart command")
    if message.from_user.id in whitelist:
        users_notifications.clear()
        send_menu_with_keyboard(message.chat.id)
    else:
        bot.send_message(message.chat.id, permission_denied_message)

# Додати перевірку whitelist до інших команд

@bot.message_handler(func=lambda message: message.text == "Витрати")
def handle_expenses(message):
    logger.info("Handling expenses")
    if message.from_user.id in whitelist:
        bot.send_message(message.chat.id, "Введіть деталі вашого витрати:")
    else:
        bot.send_message(message.chat.id, permission_denied_message)

@bot.message_handler(func=lambda message: message.text == "Налаштування")
def handle_settings(message):
    logger.info("Handling settings")
    if message.from_user.id in whitelist:
        chat_id = message.chat.id
        bot.send_message(chat_id, "Введіть час сповіщень у форматі 'година:хвилина' (наприклад, 20:24):")
        bot.register_next_step_handler(message, set_notification_time)
    else:
        bot.send_message(message.chat.id, permission_denied_message)

@bot.message_handler(func=lambda message: message.text == "Дохід")
def handle_income(message):
    logger.info("Handling income")
    if message.from_user.id in whitelist:
        bot.send_message(message.chat.id, "Введіть деталі вашого доходу:")
    else:
        bot.send_message(message.chat.id, permission_denied_message)

@bot.message_handler(func=lambda message: message.text == "Бюджет")
def handle_budget(message):
    logger.info("Handling budget")
    if message.from_user.id in whitelist:
        bot.send_message(message.chat.id, "Введіть ваш бюджет:")
    else:
        bot.send_message(message.chat.id, permission_denied_message)

def set_notification_time(message):
    logger.info("Setting notification time")
    chat_id = message.chat.id
    if message.from_user.id in whitelist:
        time_str = message.text.strip()
        try:
            hour, minute = map(int, time_str.split(':'))
            users_notifications[chat_id] = (hour, minute)
            bot.send_message(chat_id, f"Час сповіщення збережено: {hour:02d}:{minute:02d}")
            schedule_notification(hour, minute, chat_id)
        except ValueError:
            bot.send_message(chat_id, "Невірний формат часу. Введіть у форматі 'година:хвилина'.")
    else:
        bot.send_message(message.chat.id, permission_denied_message)

def schedule_notification(hour, minute, chat_id):
    logger.info(f"Scheduling notification for chat_id {chat_id} at {hour:02d}:{minute:02d}")
    scheduled_time = f"{hour:02d}:{minute:02d}"
    schedule.every().day.at(scheduled_time).do(send_notification, chat_id)

def send_notification(chat_id):
    logger.info(f"Sending notification to chat_id {chat_id}")
    try:
        bot.send_message(chat_id, "Хей! 👋\nЯ тут, щоб нагатдати тобі вказати твої витрати)")
    except Exception as e:
        logger.error(f"Error sending notification to chat_id {chat_id}: {e}")

def polling_thread():
    bot.polling(none_stop=True)

@bot.message_handler(commands=['update'])
def handle_update_button(message):
    logger.info("Checking for updates")
    if message.from_user.id in whitelist:
        version, description = get_latest_release_info()
        if version and description:
            update_message = f"*Нове оновлення*\nВерсія: *{version}*\n{description}"
            bot.send_message(message.chat.id, update_message, parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, "Немає доступних оновлень")
    else:
        bot.send_message(message.chat.id, permission_denied_message)

def polling_thread():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    polling_thread = threading.Thread(target=polling_thread)
    polling_thread.start()

    while True:
        schedule.run_pending()
        time.sleep(1)
