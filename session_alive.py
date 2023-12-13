import requests
# from blank_sheet import user_session
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ.get('TOKEN')
user_session = "0C631AFDE1C38A6CE063118A16ACD76C"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

data = {
    "IsSessionAlive": {
        "userSession": f"{user_session}"
    }
}
url = "https://ulapi.bgpb.by:8243/wso2_session/isalive/v1.1"


def session_alive(url, headers, data):
    response = requests.post(url=url, headers=headers, json=data)
    if response.ok:
        response_data = response.json()
        if response_data.get('success') == 'true' and response_data.get('result') is True:
            return True
        else:
            return False
    return False


is_session_alive = session_alive(url, headers, data)
print("Сессия активна:", is_session_alive)