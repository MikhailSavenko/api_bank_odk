from blank_sheet import main_blank_sheet
from get_count import main_get_count

BANK_ACCOUNT_WINDOW = 'BY37OLMP30130001086900000933'
BANK_ACCOUNT_CEILING = 'BY47OLMP30130009044450000933'

def authorization():
    go_main_blank_sheet = None
    max_attempts = 7
    # Выполняйте попытки авторизации
    for i in range(max_attempts):
        go_main_blank_sheet = main_blank_sheet()
        if go_main_blank_sheet is not None:
            # Успешная авторизация
            print("Успешная авторизация.")
            # Здесь добавьте код для выполнения основной логики программы
            # Например:
            process_data(go_main_blank_sheet)
            break
    else:
        # Цикл закончился без успешной авторизации
        print("Не удалось авторизоваться после", max_attempts, "попыток")
        return None


def process_data(user_session):
    """"Вызываем файл получения выписки"""
    # получаем выписки счет окна
    go_main_get_count_window = main_get_count(user_session, account=BANK_ACCOUNT_WINDOW)
    print(go_main_get_count_window)
    # запускаем функцию парсинга и затем вебхук окна
    # получаем выписки счет потолки
    go_main_get_count_ceiling = main_get_count(user_session, account=BANK_ACCOUNT_CEILING)
    print(go_main_get_count_ceiling)
    # запускаем функцию парсинга и затем вебхук потолки



if __name__ == "__main__":
    authorization()
