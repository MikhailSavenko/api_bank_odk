import re
import logging
from datetime import datetime
import requests


def parse_naznText(result_payments, account):
    extracted_data = []
    # Регулярное выражение для номера договора/счета
    contract_account_pattern = r'\b(?!(?:2022|2023|00000|2024)\b)\d{4,6}(?![/])\b'
    for payment in result_payments:
        description = payment['naznText']

        contracts_accounts = re.findall(contract_account_pattern, description)
        contract = contracts_accounts[0] if contracts_accounts else ''

        date_and_time = payment['docDate']
        datetime_object = datetime.strptime(date_and_time, "%Y-%m-%dT%H:%M:%S%z")
        date_part = datetime_object.date()
        time_part = datetime_object.time()
        date_str = date_part.strftime('%Y-%m-%d')
        time_str = time_part.strftime("%H:%M")

        extracted_data.append({
            'description': description,
            'contract': contract,
            'account': account,
            'time': time_str,
            'date': date_str,
            'amount': payment['crAmount']

        })
    logging.info(f'Готово к вебхуку {extracted_data}')
    print(extracted_data)
    return extracted_data


def post_webhook(extracted_data):
    bitrix_url = "https://crm.okna-ori.by/rest/1/5rqi5834zubf0jjj/crm.item.add?entityTypeId=163"
    success_count = 0
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
                logging.info('Сделка успешно добавлена в Битрикс')
                success_count += 1
                return True
            else:
                logging.error(f'Ошибка при добавлении сделки в Битрикс: {response.status_code}')
        return success_count == len(extracted_data)
    except requests.RequestException as e:
        logging.error(f'Ошибка сетевого запроса: {e}')
        return False