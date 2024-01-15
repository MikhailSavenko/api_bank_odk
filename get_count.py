import requests
from jsonpath_ng import parse
from dotenv import load_dotenv
import os
from payments_db import is_payment_in_txt
import logging
from exeptions import ExeptionSSOClose


load_dotenv()

PAYLOAD = os.environ.get('PAYLOAD')
TOKEN = os.environ.get('TOKEN')


def get_bank_statement(user_session, account, DATE_FROM, DATE_TO):
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
        return statement
    elif response.status_code == 500:
        logging.error(f"Ошибка при получении выписки по счетам код:{response.status_code}, json ответ: {response.json()}")
        raise ExeptionSSOClose


def extract_credit_amount(response_extract_data):
    """Достаем оплаты на счет"""
    jsonpath_expr = parse("$.result[*].extractList[*].turns[*]")
    matches = [match.value for match in jsonpath_expr.find(response_extract_data)]

    cr_amount = [i for i in matches if float(i['crAmount']) > 0]
    logging.info(f'Количество оплат всего пришло: {len(cr_amount)}')
    return cr_amount


def get_result(payments, account):
    """Достаем нужные поля по каждой оплате"""
    result_payments_not_dubble = []
    result_payments = []
    for payment in payments:
        docId = payment.get('docId', None)
        crAmount = payment.get('crAmount', None)
        naznText = payment.get('naznText', None)
        docDate = payment.get('docDate', None)
        result_payments.append({"docId": docId, "docDate": docDate, "crAmount": crAmount, "naznText": naznText})
    for payment_duble in result_payments:
        if not is_payment_in_txt(account, payment_duble):
            result_payments_not_dubble.append(payment_duble)
    return result_payments_not_dubble
    

def main_get_count(user_session, account, DATE_FROM, DATE_TO):
    try:
        result_get_bank_statement = get_bank_statement(user_session, account, DATE_FROM, DATE_TO)
        if result_get_bank_statement:
            result_extract_credit_amount = extract_credit_amount(result_get_bank_statement)
            if result_extract_credit_amount:
                return get_result(result_extract_credit_amount, account)
        return None
    except ExeptionSSOClose as e:
        logging.error(f'Поймано исключение {e}. Требуется авторизация!')
        return 'go'


if __name__ == "__main__":
    main_get_count()