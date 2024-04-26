import requests
from dotenv import load_dotenv
import os
import logging
import base64
import pdfplumber

load_dotenv()

TOKEN = os.environ.get('TOKEN')


def get_document(user_session, account, docId, date_from, date_to):
    url = 'https://ulapi.bgpb.by:8243/wso2_printform/enclosure/v1.1/'
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Host": "ulapi.bgpb.by:8243",
        "Content-Type": "application/json",
    }
    data = {
        "getEnclosure": {
            "docId": docId,
            "userSession": user_session,
            "printFormInData": {
                "printFormFileType": 2,
                "requestType": "desc",
                "account": account,
                "descFilter": {
                    "currCode": 933,
                    "rubVal": "",
                    "dateFrom": date_from,
                    "dateTo": date_to,
                    "isNazn": 1,
                    "sortByDateDoc": 1
                }
            }     
        }
    }   
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Поднимает исключение, если запрос завершается неудачно
        base64_response = response.json()
        logging.info(f'Получение приложения к оплате..')
        return base64_response
    except requests.RequestException as e:
        logging.error(f'Ошибка при запросе к API, получение приложения: {e}')
        return None


def get_text_in_docs_base64(base64_response):
    try:
        result_data = base64_response['result']
        file_name = result_data['fileName']
        printForm = result_data['printForm']

        decoded_data  = base64.b64decode(printForm)

        with open(file_name, "wb") as file:
            file.write(decoded_data)
        logging.info('Приложение pdf получено')
        return file_name
    except KeyError as e:
        logging.error(f'Ошибка при обработке ответа API: {e}')
        return None


def cleaned_data(data):
    cleaned_data_list = [[cell.replace('\n', ' ') for cell in row] for row in data]
    return cleaned_data_list


def extract_table(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        table_page = pdf.pages[1]
        data = table_page.extract_tables()[0]
        table = cleaned_data(data)
    return table


def get_payments_from_pdf(file_name):
    payments = []
    try:
        table = extract_table(file_name)
        for i in range(1, len(table)):
            amount = table[i][1]
            description = ' '.join([table[i][0], table[i][2]])
            payments.append((amount, description))
        logging.info(f'Оплаты вытянуты  из pdf')
        return payments
    except Exception as e:
        logging.warning(f'Одностраничная оплата. PDF: {e}')
        return None
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


def main_get_document(user_session, account, docId, date_from, date_to):
    try:
        doc = get_document(user_session, account, docId, date_from, date_to)
        if doc:
            pdf_base64 = get_text_in_docs_base64(doc)
            if pdf_base64:
                counts = get_payments_from_pdf(pdf_base64)
                return counts
    except Exception as e:
        logging.error(f'Неожиданная ошибка: {e}')
    return None
