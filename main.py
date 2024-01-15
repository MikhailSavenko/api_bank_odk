import datetime
import time

import requests
from dotenv import load_dotenv
import os
import schedule

from blank_sheet import main_blank_sheet
from get_count import main_get_count
from configs import configure_logging
from parse_and_hook import parse_naznText, post_webhook
from payments_db import payment_write_in_txt_a, payment_write_in_txt_w
import logging

load_dotenv()

TOKEN = os.environ.get('TOKEN')

BANK_ACCOUNT_WINDOW = 'BY37OLMP30130001086900000933'
BANK_ACCOUNT_CEILING = 'BY47OLMP30130009044450000933'
MAX_ITERATIONS = 22
SLEEP = 60*15 # сон 15 минут


class ApiBankOkd():
    def __init__(self) -> None:
        self.user_session = None 

    def authorization(self):
        max_attempts = 7
        for i in range(max_attempts):
            self.user_session = main_blank_sheet()
            if self.user_session is not None:
                return self.user_session
            else:
                logging.warning("Не удалось авторизоваться на попытке", i + 1)
        logging.error("Не удалось авторизоваться после", max_attempts, "попыток")
        return None

    def session_alive(self):
        url = "https://ulapi.bgpb.by:8243/wso2_session/isalive/v1.1"
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        } 
        data = {
            "IsSessionAlive": {
            "userSession": f"{self.user_session}"
            }
        }
        response = requests.post(url=url, headers=headers, json=data)
        if response.ok:
            response_data = response.json()
            if response_data.get('success') == 'true' and response_data.get('result') is True:
                logging.info('Сессия продлена(лог в session_alive) True')
                return True
            else:
                logging.info('Сессия не продлена(лог в session_alive) False')
                return False
        return False
    
    def get_account_statements(self, payment_write, account, date):
        go_main_get_count = main_get_count(self.user_session, account, date, date)
        if not go_main_get_count:
            if payment_write == payment_write_in_txt_w:
                payment_write(account, go_main_get_count)
                logging.info('Архив прошлого дня очищен')
            logging.info('Проверка на дубликаты выполнена. Новых зачислений нет')
            pass
        else:
            logging.info(f'Проверка на дубликаты выполнена. Есть новые зачисления. Кол-во: {len(go_main_get_count)}')
            payment_write(account, go_main_get_count)
            logging.info('Архив обновлен')
            parse = parse_naznText(go_main_get_count, account, self.user_session, date, date)
            logging.info(f'Парсинг данных выполнен, готово к вебхуку {parse}')
            post_webhook(parse)

    def process_data(self):
        """Вызываем файл получения выписки"""
        date_time_now = f'{datetime.datetime.now().date()}T00:00:00+03:00'
        date_time_yesterday = f"{datetime.datetime.now().date() - datetime.timedelta(days=1)}T00:00:00+03:00"
        
        logging.info('Запущена выгрузка за вчера окна')
        self.get_account_statements(payment_write_in_txt_a, BANK_ACCOUNT_WINDOW, date_time_yesterday)
        logging.info('Запущена выгрузка за вчера потолок')
        self.get_account_statements(payment_write_in_txt_a, BANK_ACCOUNT_CEILING, date_time_yesterday)
        
        logging.info('Запущена ПЕРВАЯ за сегодня окна')
        self.get_account_statements(payment_write_in_txt_w, BANK_ACCOUNT_WINDOW, date_time_now)
        logging.info('Запущена ПЕРВАЯ за сегодня потолки')
        self.get_account_statements(payment_write_in_txt_w, BANK_ACCOUNT_CEILING, date_time_now)
    
        time.sleep(SLEEP)

        sessia = self.session_alive()
        if sessia:
            logging.info('Сессия продлена')
        else:
            logging.error(f'Сессия не продлена. Выполняется авторизация!')
            new_session = self.authorization()
            if new_session:
                self.user_session = new_session
                logging.info('Сессия обновлена')
            else:
                logging.error(f'Обновить сессию не удалось')
                
        time.sleep(SLEEP)

        iteration_count = 0
        while iteration_count != MAX_ITERATIONS:
            iteration_count += 1
            
            logging.info('Запущена выгрузка окна(цикл)')
            self.get_account_statements(payment_write_in_txt_a, BANK_ACCOUNT_WINDOW, date_time_now)
            logging.info('Запущена выгрузка потолки(цикл)')
            self.get_account_statements(payment_write_in_txt_a, BANK_ACCOUNT_CEILING, date_time_now)
        
            time.sleep(SLEEP)

            sessia = self.session_alive()
            if sessia:
                logging.info('Сессия продлена')
            else:
                logging.error(f'Сессия не продлена. Выполняется авторизация!')
                new_session = self.authorization()
                if new_session:
                    self.user_session = new_session
                    logging.info('Сессия обновлена')
                else:
                    logging.error(f'Обновить сессию не удалось')
                
            time.sleep(SLEEP)


if __name__ == "__main__":
    configure_logging()
    api_instance = ApiBankOkd()
    schedule.every().day.at("10:53").do(api_instance.authorization)
    schedule.every().day.at("10:53").do(api_instance.process_data)

    while True:
        schedule.run_pending()
        time.sleep(1)
