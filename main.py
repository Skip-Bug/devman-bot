import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot


def check_has_review(url, token, timestamp=None):
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


def main():
    load_dotenv()

    # url = 'https://dvmn.org/api/user_reviews/'
    url = 'https://dvmn.org/api/long_polling/'
    tg_token = os.getenv('TG_BOT_TOKEN')
    token = os.getenv('DEVMAN_TOKEN')
    if not token or not tg_token:
        return
    timestamp = None
    bot = Bot(token=tg_token)

    username = os.getenv('TG_USERNAME')
    chat_id = os.getenv('TG_CHAT_ID')
    
    while True:
        try:
            review_status = check_has_review(url, token, timestamp)
            if review_status.get('status') == "found":
                timestamp = review_status.get('last_attempt_timestamp')
                bot.send_message(
                    chat_id=chat_id,
                    text=f'@{username}, Преподаватель проверил работу!'                    
                )

            elif review_status.get('status') == "timeout":
                timestamp = review_status.get('timestamp_to_request')

        except requests.exceptions.ReadTimeout:
            time.sleep(5)
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            continue



if __name__ == '__main__':
    main()
