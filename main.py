from blank_sheet import main_blank_sheet
from get_count import main_get_count
from session_alive import session_alive

import datetime
import time
import schedule
from configs import configure_logging
from parse_and_hook import parse_naznText, post_webhook
import logging

BANK_ACCOUNT_WINDOW = 'BY37OLMP30130001086900000933'
BANK_ACCOUNT_CEILING = 'BY47OLMP30130009044450000933'
user_session = None


def authorization():
    global user_session
    max_attempts = 7
    # Выполняйте попытки авторизации
    for i in range(max_attempts):
        user_session = main_blank_sheet()
        if user_session is not None:
            # Успешная авторизация
            print("Успешная авторизация.")
            return user_session
        else:
            print("Не удалось авторизоваться на попытке", i + 1)
    # Цикл закончился без успешной авторизации
    print("Не удалось авторизоваться после", max_attempts, "попыток")
    return None


def process_data():
    """Вызываем файл получения выписки"""
    global user_session
    time_start = datetime.time(8, 00, 00)
    time1 = f'T{time_start}'+'+03:00'
    date = f'{datetime.datetime.now().date()}'
    # здесь лежит дата и время последней выгрузки окон
    DATE_FROM = f"{datetime.datetime.now().date() - datetime.timedelta(days=1)}T19:00:00+03:00"
    DATE_TO = date + time1
    # получаем выписки счет окна
    go_main_get_count_window = main_get_count(user_session, BANK_ACCOUNT_WINDOW, DATE_FROM, DATE_TO)
    print(go_main_get_count_window)
    # запускаем функцию парсинга и затем вебхук окна
    parse = parse_naznText(go_main_get_count_window, BANK_ACCOUNT_WINDOW)
    logging.info(f'Выгрузка окон произошла, парсинг выполнен, готово к хуку {parse}')
    post_webhook(parse)
    logging.info(f'Вебхук окна отправлен')
    # получаем выписки счет потолки
    go_main_get_count_ceiling = main_get_count(user_session, BANK_ACCOUNT_CEILING, DATE_FROM, DATE_TO)
    print(go_main_get_count_ceiling)
    # запускаем функцию парсинга и затем вебхук потолки
    ...
    DATE_FROM = DATE_TO
    # спим 15 минут далее продлеваем сессию и спим еще 15 минут
    time.sleep(15)
    # вызов функции продления сессии 
    session_alive(user_session)
    time.sleep(15)

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
        # спим 15 минут далее продлеваем сессию
        time.sleep(15)
        # вызов функции продления сессии 
        session_alive(user_session)
        # спим еще 15 минут
        time.sleep(15)
        

if __name__ == "__main__":
    configure_logging()
    schedule.every().day.at("18:42").do(authorization)
    schedule.every().day.at("18:43").do(process_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
