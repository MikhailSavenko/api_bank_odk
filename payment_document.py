import requests
from dotenv import load_dotenv
import os
import logging
import base64
import PyPDF2
import re


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
        logging.error(f'Ошибка при запросе к API: {e}')
        return None


def get_text_in_docs_base64(base64_response):
    try:
        result_data = base64_response['result']
        file_name = result_data['fileName']
        printForm = result_data['printForm']

        decoded_data  = base64.b64decode(printForm)

        with open(f"{file_name}.pdf", "wb") as file:
            file.write(decoded_data)
        logging.info('Приложение pdf получено')
        return file_name
    except KeyError as e:
        logging.error(f'Ошибка при обработке ответа API: {e}')
        return None


def get_payments_from_pdf(file_name):
    payments = []
    previous_line = None
    try:
        with open(f'{file_name}.pdf', "rb") as f:
            pdf = PyPDF2.PdfReader(f)
            page = pdf.pages[1]
            text = page.extract_text()

        lines = text.split('\n') 
        lines = lines[6:-1]

        pattern = re.compile(r'(?P<name>[\w\s]+?)(?=\s?\d+\.\d+)\s?(?P<amount>\d+\.\d+)\s+(?P<text>.+)')
        
        for line in lines:
            print(line)
            match = pattern.match(line)
            if match:
                if previous_line:
                    name = (previous_line + (' ') + match.group('name')).strip()
                else:
                    name = match.group('name').strip()
                amount = float(match.group('amount'))
                text = match.group('text')
                naznText = (name or "") + (' ') + (text or "")
                payments.append((amount, naznText))
            else:
                previous_line = line
                logging.info(f'Длинная ФИО. Обновлен параметр previous_line. К name будет добавлено часть {previous_line}')          
        # os.remove(f'{file_name}.pdf')
        logging.info(f'Вытянуты оплаты из pdf {payments}')
        return payments
    except Exception as e:
        logging.error(f'Ошибка при обработке PDF: {e}')
        return None


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
