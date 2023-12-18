import re
import pandas as pd
import json

# Путь к файлу следует использовать pathlib

file_path = 'C:\Users\PRAGMA-PC_001\Desktop\api_bank_odk\requirements.txt'

# Чтение и загрузка данных из файла в формате JSON
with open(file_path, 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Регулярное выражение для номера договора/счета
contract_account_pattern = r'\\b(?:договору|счету|N|дог)\\s*?(\\d{4,})\\b'

# Регулярное выражение для ФИО
fio_pattern = r'\\b[A-ZА-ЯЁ][a-zа-яё-]+\\s[A-ZА-ЯЁ][a-zа-яё-]+\\s[A-ZА-ЯЁ][a-zа-яё-]+\\b'

# Обработка данных
extracted_data = []
for entry in json_data:
    text = entry['naznText'] if 'naznText' in entry else ''
    contracts_accounts = re.findall(contract_account_pattern, text, flags=re.IGNORECASE)
    names = re.findall(fio_pattern, text, flags=re.IGNORECASE)
    names = [name for name in names if name.lower() != "шахов игорь вячеславович"]
    extracted_data.append({
        'text': text,
        'contracts_accounts': contracts_accounts,
        'names': names
    })

# Показываем примеры извлеченных данных
extracted_data[:5]  # Первые 5 записей для проверки
