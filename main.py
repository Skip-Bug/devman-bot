"""Бот для проверки ревью на dvmn.org"""
import argparse
import os
import time
import logging


import requests
from dotenv import load_dotenv
from telegram import Bot


def create_parser():
    """Создает парсер для айди чата"""
    parser = argparse.ArgumentParser(
        description='Бот для проверки ревью на dvmn.org'
    )
    parser.add_argument('--id', help='caht_id чата', type=int)
    return parser


def check_has_review(url, token, timestamp=None):
    """Проверяет есть ли новые ревью"""
    headers = {'Authorization': f'Token {token}'}
    params = {'timestamp': timestamp}
    if not timestamp:
        response = requests.get(url, headers=headers, timeout=95)
    else:
        response = requests.get(
            url, headers=headers,
            timeout=95, params=params
        )

    response.raise_for_status()
    return response.json()


def send_message(bot, params):
    """Отправляет сообщение в телеграм"""
    if params['is_negative']:
        bot.send_message(
            chat_id=params['chat_id'],
            text=f"""@{params['username']},
        У вас проверили работу 
        {params['lesson_title']},
        ссылка: {params['lesson_url']},
        К сожалению, она не прошла проверку"""
        )

    else:
        bot.send_message(
            chat_id=params['chat_id'],
            text=f"""@{params['username']},
        У вас проверили работу 
        {params['lesson_title']},
        ссылка: {params['lesson_url']},
        Преподавателю все понравилось, можно приступать к следующему уроку!"""
        )


def main():

    logging.basicConfig(filename="sample.log", level=logging.INFO)

    load_dotenv()

    url = 'https://dvmn.org/api/long_polling/'
    tg_token = os.getenv('TG_BOT_TOKEN')
    token = os.getenv('DEVMAN_TOKEN')
    if not token or not tg_token:
        logging.error('Токены не найдены')
        return
    timestamp = None
    bot = Bot(token=tg_token)

    parser = create_parser()
    args = parser.parse_args()

    username = os.getenv('TG_USERNAME')
    chat_id = args.id or os.getenv('TG_CHAT_ID')

    while True:
        try:
            review_status = check_has_review(url, token, timestamp)
            if review_status.get('status') == "found":

                timestamp = review_status.get('last_attempt_timestamp')
                logging.info('Преподаватель проверил работу!')
                for attempt in review_status.get('new_attempts'):
                    lesson_title = attempt['lesson_title']
                    is_negative = attempt['is_negative']
                    lesson_url = attempt.get('lesson_url')

                    params = {
                        'username': username,
                        'chat_id': chat_id,
                        'lesson_title': lesson_title,
                        'is_negative': is_negative,
                        'lesson_url': lesson_url
                    }

                    send_message(bot, params)

            elif review_status.get('status') == "timeout":
                timestamp = review_status.get('timestamp_to_request')

        except requests.exceptions.ReadTimeout:
            time.sleep(5)
            logging.error('Превышено время ожидания')
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            logging.error('Ошибка соединения')
            continue


if __name__ == '__main__':
    main()
