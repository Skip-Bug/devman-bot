import os
import pprint
import time

import requests
from dotenv import load_dotenv


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
    token = os.getenv('DEVMAN_TOKEN')
    timestamp = None
    while True:
        try:
            review_status = check_has_review(url, token, timestamp)
            print('Результат запроса:')
            pprint.pprint(review_status)
            print()
            if review_status.get('status') == "found":
                timestamp = review_status.get('last_attempt_timestamp')
            elif review_status.get('status') == "timeout":
                timestamp = review_status.get('timestamp_to_request')

        except requests.exceptions.ReadTimeout:
            time.sleep(5)
            print('Попытаемся еще раз')
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            print('Попытаемся еще раз')
            continue        
        except KeyboardInterrupt:
            print('Остановленно пользователем')
            break


if __name__ == '__main__':
    main()
