from blank_sheet import main_blank_sheet
from get_count import main_get_count

import datetime
import time
import schedule

BANK_ACCOUNT_WINDOW = 'BY37OLMP30130001086900000933'
BANK_ACCOUNT_CEILING = 'BY47OLMP30130009044450000933'
user_session = None


def authorization():
    global user_session
    go_main_blank_sheet = None
    max_attempts = 7
    # Выполняйте попытки авторизации
    for i in range(max_attempts):
        go_main_blank_sheet = main_blank_sheet()
        if go_main_blank_sheet is not None:
            # Успешная авторизация
            print("Успешная авторизация.")
            user_session = go_main_blank_sheet
            return user_session
    else:
        # Цикл закончился без успешной авторизации
        print("Не удалось авторизоваться после", max_attempts, "попыток")
        return None


def process_data():
    """"Вызываем файл получения выписки"""
    global user_session
    time_start = datetime.time(8, 00, 00)
    time1 = f'T{time_start}'+"+03:00"
    date = f'{datetime.datetime.now().date()}'
    # здесь лежит дата и время последней выгрузки окон
    DATE_FROM = f"{datetime.datetime.now().date() - datetime.timedelta(days=1)}T19:00:00+03:00"
    DATE_TO = date + time1
    # получаем выписки счет окна
    go_main_get_count_window = main_get_count(user_session, BANK_ACCOUNT_WINDOW, DATE_FROM, DATE_TO)
    print(go_main_get_count_window)
    # запускаем функцию парсинга и затем вебхук окна
    ...
    # получаем выписки счет потолки
    go_main_get_count_ceiling = main_get_count(user_session, BANK_ACCOUNT_CEILING, DATE_FROM, DATE_TO)
    print(go_main_get_count_ceiling)
    # запускаем функцию парсинга и затем вебхук потолки
    ...
    DATE_FROM = DATE_TO
    time.sleep(10)
    DATE_TO = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z") + "+03:00"

    while DATE_TO != date + 'T19:00:00+03:00':
        DATE_TO = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z") + "+03:00"
        # получаем выписки счет окна
        go_main_get_count_window = main_get_count(user_session, BANK_ACCOUNT_WINDOW, DATE_FROM, DATE_TO)
        print(go_main_get_count_window)
        # запускаем функцию парсинга и затем вебхук окна
        ...
        # получаем выписки счет потолки
        go_main_get_count_ceiling = main_get_count(user_session, BANK_ACCOUNT_CEILING, DATE_FROM, DATE_TO)
        print(go_main_get_count_ceiling)
        # запускаем функцию парсинга и затем вебхук потолки
        ...
        DATE_FROM = DATE_TO
        time.sleep(10)
        

if __name__ == "__main__":
    schedule.every().day.at("17:49").do(authorization)
    schedule.every().day.at("17:50").do(process_data)

    while True:
        schedule.run_pending()
        time.sleep(1)
