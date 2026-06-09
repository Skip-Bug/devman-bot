from telegram import Bot
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    token = os.getenv('TG_BOT_TOKEN')
    if not token:
        return
    bot = Bot(token=token)
    updates = bot.get_updates()
    print(updates[-1])
    bot.send_message(text='Привет Леонид!', chat_id=5133218174)


if __name__ == '__main__':
    main()
