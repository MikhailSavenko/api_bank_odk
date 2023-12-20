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
SLEEP = 60*5


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
    time_start = datetime.time(17, 54, 0)
    time1 = f'T{time_start}'+'+03:00'
    date = f'{datetime.datetime.now().date()}'
    
    DATE_FROM = f"{datetime.datetime.now().date() - datetime.timedelta(days=1)}T18:50:00+03:00"
    logging.info(f'date from {DATE_FROM}')
    DATE_TO = date + time1
    logging.info(f'date to {DATE_TO}')
    
    go_main_get_count_window = main_get_count(user_session, BANK_ACCOUNT_WINDOW, DATE_FROM, DATE_TO)
    logging.info('Получена Первая за день выписка по окнам')
    parse = parse_naznText(go_main_get_count_window, BANK_ACCOUNT_WINDOW)
    logging.info(f'Выгрузка окон произошла, парсинг выполнен, готово к хуку {parse}')
    post_webhook(parse)
    logging.info(f'Вебхук окна отправлен')

    go_main_get_count_ceiling = main_get_count(user_session, BANK_ACCOUNT_CEILING, DATE_FROM, DATE_TO)
    logging.info('Получена Первая за день выписка по потолкам')
    parse = parse_naznText(go_main_get_count_ceiling, BANK_ACCOUNT_CEILING)
    logging.info(f'Выгрузка потолков произошла, парсинг выполнен, готово к хуку {parse}')
    post_webhook(parse)
    logging.info(f'Вебхук потолки отправлен')
   
    time.sleep(SLEEP)
    
    session_on = session_alive(user_session)
    logging.info(f'Сессия продлена {session_on}')

    time.sleep(SLEEP)
    
    max_iterations = 22
    iteration_count = 0
    while iteration_count != max_iterations:
        DATE_FROM = DATE_TO
        logging.info(f'date from {DATE_FROM}')
        DATE_TO = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z") + "+03:00"
        logging.info(f'date to {DATE_TO}')
        go_main_get_count_window = main_get_count(user_session, BANK_ACCOUNT_WINDOW, DATE_FROM, DATE_TO)
        logging.info('Получена выписка окна(цикл)')
        parse = parse_naznText(go_main_get_count_window, BANK_ACCOUNT_WINDOW)
        logging.info(f'Парсинг выполнен, готово к хуку(цикл) {parse}')
        post_webhook(parse)
        logging.info(f'Вебхук окна отправлен(цикл)')
        
        go_main_get_count_ceiling = main_get_count(user_session, BANK_ACCOUNT_CEILING, DATE_FROM, DATE_TO)
        logging.info('Получена выписка потолки(цикл)')
        parse = parse_naznText(go_main_get_count_ceiling, BANK_ACCOUNT_CEILING)
        logging.info(f'Парсинг выполнен, готово к хуку(цикл) {parse}')
        post_webhook(parse)
        logging.info(f'Вебхук потолки отправлен(цикл)')
        
        time.sleep(SLEEP)

        session_on = session_alive(user_session)
        logging.info(f'Сессия продлена {session_on}')

        time.sleep(SLEEP)


if __name__ == "__main__":
    configure_logging()
    schedule.every().day.at("17:53").do(authorization)
    schedule.every().day.at("17:54").do(process_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
