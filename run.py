import requests
import json

request_endpoint = 'https://api.notion.com/v1/databases/'
database_id = '9d353db84aac400aa53190c88f66e2a4'

secret_dict = json.load(open('secrets.json', 'r'))
headers = {"Authorization": f"Bearer {secret_dict['token']}"}

print(requests.get(request_endpoint+database_id, headers=headers).json())
