import requests
from api_bankGo import user_session


token = "e6e53aea-467a-30a4-901a-3394482b7404"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

data = {
    "IsSessionAlive": {
        "userSession": user_session
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