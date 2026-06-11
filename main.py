"""Бот для проверки ревью на dvmn.org"""
import os
import time
import logging


import requests
from dotenv import load_dotenv
from telegram import Bot


def check_has_review(token, timestamp=None):
    """Проверяет есть ли новые ревью"""
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': f'Token {token}'}
    params = {'timestamp': timestamp} if timestamp else None

    response = requests.get(url, headers=headers, timeout=5, params=params)

    response.raise_for_status()
    return response.json()


def send_message(bot, bot_params):
    """Отправляет сообщение в телеграм"""

    if bot_params['is_negative']:
        status = 'К сожалению, она не прошла проверку'

    else:
        status = (
            'Преподавателю все понравилось, можно приступать к следующему уроку!'
        )
    text = (
        f"@{bot_params['username']},\n"
        f"У вас проверили работу\n"
        f"{bot_params['lesson_title']},\n"
        f"ссылка: {bot_params['lesson_url']},\n"
        f"{status}"
    )

    bot.send_message(chat_id=bot_params['chat_id'], text=text)


def main():
    load_dotenv()
    logging.basicConfig(
        filename="sample.log",
        level=logging.INFO,
        encoding='utf-8'
    )

    tg_token = os.environ['TG_BOT_TOKEN']
    token = os.environ['DEVMAN_TOKEN']
    username = os.environ['TG_USERNAME']
    chat_id = os.environ['TG_CHAT_ID']

    timestamp = None
    bot = Bot(token=tg_token)

    while True:
        try:
            review_status = check_has_review(token, timestamp)
            if review_status.get('status') == "found":

                timestamp = review_status.get('last_attempt_timestamp')
                logging.info('Преподаватель проверил работу!')
                for attempt in review_status.get('new_attempts'):
                    lesson_title = attempt['lesson_title']
                    is_negative = attempt['is_negative']
                    lesson_url = attempt.get('lesson_url')

                    bot_params = {
                        'username': username,
                        'chat_id': chat_id,
                        'lesson_title': lesson_title,
                        'is_negative': is_negative,
                        'lesson_url': lesson_url
                    }

                    send_message(bot, bot_params)

            elif review_status.get('status') == "timeout":
                timestamp = review_status.get('timestamp_to_request')

        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            logging.error('Ошибка соединения')
            continue


if __name__ == '__main__':
    main()
