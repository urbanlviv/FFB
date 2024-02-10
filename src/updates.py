from google_sheets import GoogleSheets
import telebot

class UpdatesHandler:
    def __init__(self, bot, spreadsheet_id):
        self.bot = bot
        self.sheets_client = GoogleSheets(spreadsheet_id)

    def handle_updates(self, message):
        if message.text == 'Update':
            # Отримуємо дані з останнього рядка таблиці
            last_row = self.sheets_client.get_last_row("A:B")
            if last_row:
                version, description = last_row[0], last_row[1]
                update_text = f"Оновлення версії: {version}\nОпис: {description}"
                self.bot.send_message(message.chat.id, update_text)
            else:
                self.bot.send_message(message.chat.id, "Таблиця порожня.")
        else:
            self.bot.send_message(message.chat.id, "Виберіть команду /start, щоб побачити кнопку 'Update'.")
