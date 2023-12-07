import requests
from jsonpath_ng import jsonpath, parse

from get_sid_selenium_headless import auth_sid
from dotenv import load_dotenv
import os


load_dotenv()

token = os.environ.get('TOKEN')

bank_account_window = 'BY37OLMP30130001086900000933'
bank_account_ceiling = 'BY47OLMP30130009044450000933'

# когда клиент авторизуется подставить кук auth_sid
auth_sid = auth_sid

# После получения sid прохоим авторизацию
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}



auth_url = "https://ulapi.bgpb.by:8243/wso2_clients/v1.1/"
data1 = {
    "IdentificationBySSOSessionId": {
    "ssoSessionId": f"{auth_sid}"
    }
}

# пытаемся получить ClientId
response = requests.post(auth_url, headers=headers, json=data1)

if response.status_code == 200:
    client_id = response.json().get('result')['clientList'][0]['clientId']
    print(client_id)
else:
    print("Ошибка при запросе:", response.status_code)



# авторизуемся использую ClientId и auth_sid
url_login = "https://ulapi.bgpb.by:8243/wso2_login/v1.1/"
data2 = {    
    "AuthorizationBySSOSessionId": {
    "clientId": client_id,
    "ssoSessionId": f"{auth_sid}"
    }
}
# открытия сессии и получения ее идентификатора (UserSession) 
response = requests.post(url_login, headers=headers, json=data2)
if response.status_code == 200:
    user_session = response.json()["result"]["userSession"]
    print(f'Авторизация успешна UserSession: {user_session}')
else:
    print("Ошибка при авторизации, код:", response.status_code)



# получение списка доступных счетов и достаем оттуда currCode для двух счетов 
url_account_list = "https://ulapi.bgpb.by:8243/wso2_account/v1.1/"
data3 = {
    "getAccountsList": {
    "filter": {
      "currencyType": 0,
      "withDetails": 1,
      "operType": 2
    },
    "userSession": f"{user_session}"
  }

}
# следует разобраться какие счета прихоят и сохранять curr_code только нужных!
curr_code_list = {}
response = requests.post(url=url_account_list, headers=headers, json=data3)
if response.status_code == 200:
    # тут я получаю список аккаунтов
    accounts = response.json().get("result", {}).get('vAcc', [])
    for account in accounts:
        if account['accNumber'] == bank_account_window:
            curr_code_window = account['currCode']
            curr_code_list['curr_code_window'] = curr_code_window
        elif account['accNumber'] == bank_account_ceiling:
            curr_code_ceiling = account['currCode']
            curr_code_list['curr_code_ceiling'] = curr_code_ceiling
        else:
            print('Счетов Окна и Потолки нет в списке') 
    print(f'Полученые currCodes{curr_code_list}')
else:
    print("Список счетов не получен:", response.status_code)


# словарь curr_code_list хранит 
# получение выписки по счетам
# BY37OLMP30130001086900000933  Окна
# BY47OLMP30130009044450000933  Потолки
data4 = {
    "getDescList": {
    "descInData": {
      "sortByDateDoc": 1,
      "isNazn": 1,
      # дата с какого изменить
       "dateFrom": "2017-05-21T15:46:14+03:00",
    # по какое число изменить
    "dateTo": "2018-05-21T15:45:53+03:00",
      "accList": [
                {
                    "accNumber": bank_account_window,
                    "currCode": curr_code_list[curr_code_window],
                    "rubVal": ""
                },
                {
                    "accNumber": bank_account_ceiling,
                    "currCode": curr_code_list[curr_code_ceiling],
                    "rubVal": ""
                }
      ]
    },
    "userSession": user_session
  }

}
url_extract = "https://ulapi.bgpb.by:8243/wso2_desc/v1.1/"
response = requests.post(url_extract, headers=headers, json=data4)
if response.status_code == 200:
    response_extract_data = response.json()
else:
    print("Не уалось получение выписки по счетам ", response.status_code)


# Достаем поступления на счет
jsonpath_expr = parse("$.result[*].extractList[*].turns[*]")
matches = [match.value for match in jsonpath_expr.find(response_extract_data)]

cr_amount = []
for i in matches:
    if float(i['crAmount']) > 0:
      cr_amount.append(i)
print(cr_amount)

