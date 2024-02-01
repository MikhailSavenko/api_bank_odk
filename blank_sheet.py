import requests
from dotenv import load_dotenv
import os
import time
import logging
from requests.exceptions import RequestException

load_dotenv()

PAYLOAD = os.environ.get('PAYLOAD')
TOKEN = os.environ.get('TOKEN')
CLIENT_ID = os.environ.get('CLIENT_ID')

session = requests.Session()


def authentication():
    """Аутентификация. Получаем SID код"""
    url = "https://www.e-bgpb.by/sso/!ClientAuth.Authentication?auth_gui=full"
    payload = PAYLOAD
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.e-bgpb.by',
        'Pragma': 'no-cache',
        'Referer': 'https://www.e-bgpb.by/sso/!ClientAuth.Login?auth_return_url=https://ulapi.bgpb.by:8243',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }
    try:
        response = session.post(url, headers=headers, data=payload)
        if response.ok:
            auth_sid = response.cookies.get('auth_sid')
            logging.info(f'SID получен: {auth_sid}')
            return auth_sid
        else:
            logging.error(f'Не удалос получить SID/ статус код {response.status_code}/ ответ json: {response.text}')
            return None
    except RequestException as e:
        logging.exception(f'Произошла ошибка при соединении или запросе Аутентификации: {e}', exc_info=True, stack_info=True)
        return None
    

def authorization(auth_sid, client_id, token):
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
    try:
        response_login = session.post(url_login, headers=headers, json=data_login)
        if response_login.status_code == 200:
            user_session = response_login.json()["result"]["userSession"]
            logging.info(f'Успешная авторизация. UserSession: {user_session}')
            return user_session
        logging.error(f"Ошибка авторизации статус код: {response_login.status_code}, ответ json: {response_login.json()}")
        return None
    except RequestException as e:
        logging.exception(f'Произошла ошибка при соединении или запросе Авторизации {e}', exc_info=True, stack_info=True)


def main_blank_sheet():
    auth_sid = authentication()
    if auth_sid:
        user_session = authorization(auth_sid, CLIENT_ID, TOKEN)
        return user_session
    return None


if __name__ == "__main__":
    main_blank_sheet()


