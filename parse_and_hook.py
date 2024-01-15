import re
import logging
from datetime import datetime
import requests
from payment_document import main_get_document


def parse_naznText(result_payments, account, user_session, date_from , date_to):
    extracted_data = []
    # Регулярное выражение для номера договора/счета
    contract_account_pattern = r'\b(?!(?:200[0-9]|201[0-4]|202[0-4]|00000)\b)N?(\d{4,6})(?![/])\b'
    for payment in result_payments:
        date_and_time = payment['docDate']
        datetime_object = datetime.strptime(date_and_time, "%Y-%m-%dT%H:%M:%S%z")
        date_part = datetime_object.date()
        time_part = datetime_object.time()
        date_str = date_part.strftime('%Y-%m-%d')
        time_str = time_part.strftime("%H:%M")
        description = payment['naznText']
        if description == 'Принятые платежи согласно реестру':
            logging.info(f"Получена оплата с ПРИЛОЖЕНИЕМ {payment['docId']}/ {description}/ {payment['crAmount']}")
            counts = main_get_document(user_session, account, payment['docId'], date_from, date_to)
            logging.info(f'counts = {counts}')
            if counts is not None:
                for count in counts:
                    logging.info(f'counts = {count}')
                    description = count[1]
                    amount = count[0]
                    contracts_accounts = re.findall(contract_account_pattern, description)
                    contract = contracts_accounts[0] if contracts_accounts else ''
                    
                    extracted_data.append({
                        'description': description,
                        'contract': contract,
                        'account': account,
                        'time': time_str,
                        'date': date_str,
                        'amount': amount
                    })
                logging.info(f'Платежи из pdf добавлены в общий список на отправку в crm. Их количество: {len(counts)}')
            else:
                logging.warning('Не удалось получить данные из pdf. Пропускаем запись в общий список.')
        else:
            contracts_accounts = re.findall(contract_account_pattern, description)
            contract = contracts_accounts[0] if contracts_accounts else ''

            extracted_data.append({
                'description': description,
                'contract': contract,
                'account': account,
                'time': time_str,
                'date': date_str,
                'amount': payment['crAmount']

            })
    logging.info(f'Всего оплат будет отправлено {len(extracted_data)}')
    return extracted_data


def post_webhook(extracted_data):
    bitrix_url = "https://crm.okna-ori.by/rest/1/5rqi5834zubf0jjj/crm.item.add?entityTypeId=163"
    success_count = 0
    failed_transactions = []
    try:
        for payment in extracted_data:
            payload = {
                "fields[ufCrm7_1692687429532]": payment['description'],
                "fields[ufCrm7_1692687312468]": payment['account'],
                "fields[ufCrm7_1692687348218]": payment['date'],
                "fields[ufCrm7_1692705471573]": payment['contract'],
                "fields[ufCrm7_1692686895896]": payment['amount'],
                "fields[ufCrm7_1692690842173]": payment['time']
            }

            response = requests.post(bitrix_url, data=payload)

            if response.ok:
                success_count += 1
            else:
                logging.error(f'Ошибка при добавлении сделки в Битрикс: {response.status_code}')
        logging.info('Сделки успешно добавлены в Битрикс')
        if failed_transactions:
            logging.warning(f'Не удалось добавить следующие сделки: {failed_transactions}')
        return success_count == len(extracted_data)
    
    except requests.RequestException as e:
        logging.error(f'Ошибка сетевого запроса: {e}')
        return False