import re
import pandas as pd
import json

# Путь к файлу следует использовать pathlib

file_path = 'windowpayments.txt'

# Чтение и загрузка данных из файла в формате JSON
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Регулярное выражение для номера договора/счета
contract_account_pattern = r'\\b(?:договору|счету|N|дог)\\s*?(\\d{4,})\\b'

# Обработка данных
extracted_data = []
for entry in json_data:
    description = entry['naznText'] if 'naznText' in entry else ''
    contracts_accounts = re.findall(contract_account_pattern, description, flags=re.IGNORECASE)
    extracted_data.append({
        'description': description,
        'contracts_accounts': contracts_accounts,
    })

# Показываем примеры извлеченных данных
extracted_data[:5]  # Первые 5 записей для проверки
