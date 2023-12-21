import requests
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()

PAYLOAD = os.environ.get('PAYLOAD')
TOKEN = os.environ.get('TOKEN')
BANK_ACCOUNT_WINDOW = 'BY37OLMP30130001086900000933'
BANK_ACCOUNT_CEILING = 'BY47OLMP30130009044450000933'

session = requests.Session()


def get_auth_sid():
    """Аутентификация. Получаем SID код"""
    url = "https://www.e-bgpb.by/sso/!ClientAuth.Authentication?auth_gui=full"
    payload = PAYLOAD
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.e-bgpb.by',
        'Referer': 'https://www.e-bgpb.by/sso/!ClientAuth.Login?auth_return_url=https://ulapi.bgpb.by:8243',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    response = session.post(url, headers=headers, data=payload)
    if response.ok:
        auth_sid = response.cookies.get('auth_sid')
        logging.info(f'SID получен: {auth_sid}')
        return auth_sid
    else:
        return None


def get_client_id(auth_sid):
    """Получение идентификатора необходимой организации (сlientId)"""
    auth_url = "https://ulapi.bgpb.by:8243/wso2_clients/v1.1/"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Length": "83",
        "Host": "ulapi.bgpb.by:8243",
        "Content-Type": "application/json",
    }
    data1 = {
        "IdentificationBySSOSessionId": {
        "ssoSessionId": f"{auth_sid}"
        }
    }
    response = session.post(auth_url, headers=headers, json=data1)

    if response.status_code == 200:
        client_id = response.json().get('result', {}).get('clientList', [{}])[0].get('clientId')
        logging.info(f"Получен clientId {client_id}")
        return client_id
    else:
        logging.error(f"Ошибка при запросе получения clientId статус:{response.status_code}, ответ json: {response.json()}")
        return None
    

def authenticate_user(auth_sid, client_id, token):
    """Прохождения авторизации, открытие сессии и получения ее идентификатора"""
    time.sleep(5)
    url_login = "https://ulapi.bgpb.by:8243/wso2_login/v1.1/"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data_login = {
        "AuthorizationBySSOSessionId": {
            "clientId": f"{client_id}",
            "ssoSessionId": f"{auth_sid}"
        }
    }

    response_login = session.post(url_login, headers=headers, json=data_login)

    if response_login.status_code == 200:
        user_session = response_login.json()["result"]["userSession"]
        logging.info(f'Успешная авторизация. UserSession: {user_session}')
        return user_session
    logging.error(f"Ошибка авторизации статус код: {response_login.status_code}, ответ json: {response_login.json()}")
    return None


def main_blank_sheet():
    auth_sid = get_auth_sid()
    if auth_sid:
        client_id = get_client_id(auth_sid)
        if client_id:
            user_session = authenticate_user(auth_sid, client_id, TOKEN)
            return user_session
    return None


if __name__ == "__main__":
    main_blank_sheet()