import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ.get('TOKEN')


def session_alive(user_session):
    url = "https://ulapi.bgpb.by:8243/wso2_session/isalive/v1.1"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    } 
    data = {
        "IsSessionAlive": {
        "userSession": f"{user_session}"
        }
    }
    response = requests.post(url=url, headers=headers, json=data)
    if response.ok:
        response_data = response.json()
        if response_data.get('success') == 'true' and response_data.get('result') is True:
            return True
        else:
            return False
    return False
