import re
import logging
from datetime import datetime


def parse_naznText(result_payments, account):
    # Обработанные данных
    extracted_data = []
    # Регулярное выражение для номера договора/счета
    contract_account_pattern = r'\b(?!(?:2022|2023|00000)\b)\d{4,6}(?![/])\b'
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
            'id': payment['docId'],
            'account': account,
            'time': time_str,
            'date': date_str,
            'amount': payment['crAmount']

        })
    logging.info(f'Готово к вебхуку {extracted_data}')
    print(extracted_data)
    return extracted_data


