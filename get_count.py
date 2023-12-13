import requests
from jsonpath_ng import jsonpath, parse
from dotenv import load_dotenv
import os
import time

load_dotenv()

PAYLOAD = os.environ.get('PAYLOAD')
TOKEN = os.environ.get('TOKEN')
BANK_ACCOUNT_WINDOW = 'BY37OLMP30130001086900000933'
BANK_ACCOUNT_CEILING = 'BY47OLMP30130009044450000933'



def get_counts():
    """Доступные счета"""
    user_session = "0C5610551A917AF6E063118A16ACD947"
    url = "https://ulapi.bgpb.by:8243/wso2_account/v1.1/"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Length": "1362",
        "Host": "ulapi.bgpb.by:8243",
        "Content-Type": "application/json",
        
    }
    data = {
        "getAccountsList": {
        "filter": {
            "currencyType": 0,
            "withDetails": 1,
            "operType": 2
        },
        "userSession": f"{user_session}"
        }
    }
    response = requests.post(url=url, headers=headers, json=data)
    if response.status_code == 200:
        counts = response.json()
        print(counts)
    else:
        print("Ошибка при запросе:", response.status_code)
        print(f'Ответ json: {response.json()}')
        return None


def get_bank_statement(user_session):
    """Получение выписки по счетам за определенный период"""
    url_extract = "https://ulapi.bgpb.by:8243/wso2_desc/v1.1/"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Length": "402",
        "Host": "ulapi.bgpb.by:8243",
        "Content-Type": "application/json",
    }
    data = {
        "getDescList": {
            "descInData": {
                "sortByDateDoc": 1,
                "isNazn": 1,
                "dateFrom": "2023-12-12T09:00:00+03:00",
                "dateTo": "2023-12-13T15:45:53+03:00",
                "accList": [
                    {
                        "accNumber": f"{BANK_ACCOUNT_WINDOW}",
                        "currCode": "933",
                        "rubVal": ""
                    },
                    {
                        "accNumber": f"{BANK_ACCOUNT_CEILING}",
                        "currCode": "933",
                        "rubVal": ""
                    }
                ]
            },
            "userSession": f"{user_session}"
        }
    }
    response = requests.post(url_extract, headers=headers, json=data)

    if response.status_code == 200:
        statement = response.json()
        print(statement)
        return statement
    else:
        print("Ошибка при получении выписки по счетам:", response.status_code)
        print(response.json())
        return None


def extract_credit_amount(response_extract_data):
    jsonpath_expr = parse("$.result[*].extractList[*].turns[*]")
    matches = [match.value for match in jsonpath_expr.find(response_extract_data)]

    cr_amount = [i for i in matches if float(i['crAmount']) > 0]
    print(cr_amount)
    return cr_amount


if __name__ == "__main__":
    user_session = "0C5610551A917AF6E063118A16ACD947"
    get_bank_statement = get_bank_statement(user_session)
    if get_bank_statement:
        extract_credit_amount(get_bank_statement)