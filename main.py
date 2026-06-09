import os
import pprint
import requests
from dotenv import load_dotenv

load_dotenv()

# url = 'https://dvmn.org/api/user_reviews/'
url = 'https://dvmn.org/api/long_polling/'
token = os.getenv('TOKEN')
headers = {'Authorization': f'Token {token}'}
response = requests.get(url, headers=headers, timeout=95)
response.raise_for_status()

response_json = response.json()
pprint.pprint(response_json)


