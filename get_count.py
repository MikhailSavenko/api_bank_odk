import requests
from jsonpath_ng import jsonpath, parse
from dotenv import load_dotenv
import os

load_dotenv()

PAYLOAD = os.environ.get('PAYLOAD')
TOKEN = os.environ.get('TOKEN')

DATE_FROM = "2023-12-09T00:00:00+03:00"
DATE_TO = "2023-12-10T17:00:00:00+03:00"


def get_bank_statement(user_session, account):
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
                "dateFrom": DATE_FROM,
                "dateTo": DATE_TO,
                "accList": [
                    {
                        "accNumber": f"{account}",
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
        # print(statement)
        return statement
    else:
        print("Ошибка при получении выписки по счетам:", response.status_code)
        print(response.json())
        return None


def extract_credit_amount(response_extract_data):
    """Достаем оплаты на счет"""
    jsonpath_expr = parse("$.result[*].extractList[*].turns[*]")
    matches = [match.value for match in jsonpath_expr.find(response_extract_data)]

    cr_amount = [i for i in matches if float(i['crAmount']) > 0]
    print(len(cr_amount))
    return cr_amount


def get_result(payments):
    """Достаем нужные поля по каждой оплате"""
    result_payments = []
    for payment in payments:
        # добавить проверку на дубликаты docId
        name = None
        countract_numbers = None
        crAmount = payment.get('crAmount', None)
        naznText = payment.get('naznText', None)
        docId = payment.get('docId', None)
        docDate = payment.get('docDate', None)
        result_payments.append({"docId": docId, "docDate": docDate, "crAmount": crAmount, "naznText": naznText, "name": name, "countract_numbers": countract_numbers})
    # print(result_payments)
    return result_payments


def main_get_count(user_session, account):
    result_get_bank_statement = get_bank_statement(user_session, account)
    if result_get_bank_statement:
        result_extract_credit_amount = extract_credit_amount(result_get_bank_statement)
        if result_extract_credit_amount:
            return get_result(result_extract_credit_amount)
    return None


if __name__ == "__main__":
    main_get_count()