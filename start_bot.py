from telegram import Bot
from dotenv import load_dotenv
import os
from pprint import pprint


def main():
    load_dotenv()
    token = os.getenv('TG_BOT_TOKEN')
    if not token:
        return
    bot = Bot(token=token)
    updates = bot.get_updates()
    update = updates[-1]

    username = update.message.chat.username
    chat_id = update.message.chat.id
    bot.send_message(chat_id=chat_id, text=f'Привет! @{username}')


if __name__ == '__main__':
    main()
