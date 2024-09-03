import json
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()

BASE_DIR = Path(__file__).parent


def is_payment_in_txt(account, payment_to_check):
    if account == os.getenv('BANK_ACCOUNT_WINDOW'):
        account = 'window'
    elif account == os.getenv('BANK_ACCOUNT_CEILING'):
        account = 'ceiling'
        
    file_name = f"{account}payments.txt"
    folder = BASE_DIR / 'data'
    folder.mkdir(exist_ok=True)
    file_path = folder / file_name
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            payments_data = json.load(file)
            if payment_to_check in payments_data:
                return True
    except FileNotFoundError:
        return False
    return False


def payment_write_in_txt_w(account, result_payments):
    """Создает новый пустой файл"""
    # Новая проверка, чтобы не записывался null
    if result_payments is None or not result_payments:
        result_payments = []
    if account == os.getenv('BANK_ACCOUNT_WINDOW'):
        account = 'window'
    elif account == os.getenv('BANK_ACCOUNT_CEILING'):
        account = 'ceiling'

    file_name = f"{account}payments.txt"
    folder = BASE_DIR / 'data'
    folder.mkdir(exist_ok=True)
    file_path = folder / file_name
    payment_data_str = json.dumps(result_payments, ensure_ascii=False)

    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(payment_data_str)

    return payment_data_str


def payment_write_in_txt_a(account, result_payments):
    """Работает как режим 'a' - добавление в конец файла."""
    if account == os.getenv('BANK_ACCOUNT_WINDOW'):
        account = 'window'
    elif account == os.getenv('BANK_ACCOUNT_CEILING'):
        account = 'ceiling'

    file_name = f"{account}payments.txt"
    folder = BASE_DIR / 'data'
    folder.mkdir(exist_ok=True)
    file_path = folder / file_name

    # Прочитать существующий файл, если он существует
    existing_data = []
    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        pass  # Если файл не существует, продолжить с пустым списком

    # Добавить новые данные
    existing_data.extend(result_payments)

    # Записать обновленные данные в файл
    with open(file_path, 'w', encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False)

    return json.dumps(result_payments, ensure_ascii=False)