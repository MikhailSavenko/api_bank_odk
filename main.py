from datetime import datetime
import time
from datetime import timedelta

from requests.exceptions import RequestException
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

TIME_AUTHORIZ = os.getenv('TIME_AUTHORIZ')
TIME_PROCESS = os.getenv('TIME_PROCESS')
time_authoriz = datetime.strptime(TIME_AUTHORIZ, '%H:%M').time()
time_process = datetime.strptime(TIME_PROCESS, '%H:%M').time()

BANK_ACCOUNT_WINDOW = os.getenv('BANK_ACCOUNT_WINDOW')
BANK_ACCOUNT_CEILING = os.getenv('BANK_ACCOUNT_CEILING')
MAX_ITERATIONS = 21
SLEEP = 60*15 # сон 15 минут


class ApiBankOkd():
    def __init__(self) -> None:
        self.user_session = None 
        
    def authorization(self):
        max_attempts = 3
        try:
            for i in range(max_attempts):
                user_session = main_blank_sheet()
                if user_session:
                    self.user_session = user_session
                    logging.info(f"US в main authorization: {self.user_session}")
                    return self.user_session
                else:
                    logging.warning(f"Не удалось авторизоваться на попытке {i}")
                    time.sleep(180)
            logging.error(f"Не удалось авторизоваться после {max_attempts} попыток")
            return None
        except Exception as e:
            logging.error(f"Ошибка в методе authorization: {e}", exc_info=True, stack_info=True)
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
        try:
            logging.info(f'Продление сессии параметр usersession: {self.user_session}')
            response = requests.post(url=url, headers=headers, json=data)
            if response.ok:
                response_data = response.json()
                if response_data.get('success') == 'true' and response_data.get('result') is True:
                    logging.info(f'Сессия продлена(лог в session_alive) True {response_data}')
                    return True
                else:
                    logging.info('Сессия не продлена(лог в session_alive) False. Выполняется авторизация!')
                    new_session = self.authorization()
                    if new_session:
                        self.user_session = new_session
                        logging.info('Сессия обновлена')
                        return True
                    else:
                        logging.error(f'Обновить сессию не удалось')
            return False
        except RequestException as e:
            logging.error(f'Ошибка при соединении или запросе session_alive {e}', exc_info=True, stack_info=True)
            return False
        except Exception as e:
            logging.error(f"Ошибка в методе session_alive: {e}")
            return False
        
    def get_account_statements(self, payment_write, account, date):
        go_main_get_count = main_get_count(self.user_session, account, date, date)
        if not go_main_get_count:
            if payment_write == payment_write_in_txt_w:
                payment_write(account, go_main_get_count)
                logging.info(f'Новый архив создан')
            logging.info('Проверка на дубликаты выполнена. Новых зачислений нет')
            pass
        elif go_main_get_count == 'go':
            self.authorization()
            logging.info('Выполняется авторизация(go)')
        else:
            logging.info(f'Проверка на дубликаты выполнена. Есть новые зачисления. Кол-во: {len(go_main_get_count)}')
            parse = parse_naznText(go_main_get_count, account, self.user_session)
            logging.info(f'Парсинг данных выполнен, готово к вебхуку {parse}')
            post_wh = post_webhook(parse)
            if post_wh:
                payment_write(account, go_main_get_count)
                logging.info('Архив обновлен')
            else:
                logging.info('Архив не обновлялся')

    def process_data(self):
        """Вызываем файл получения выписки"""
        date_time_today = f'{datetime.now().date()}T00:00:00+03:00'
        date_time_yesterday = f"{datetime.now().date() - timedelta(days=1)}T00:00:00+03:00"
        time_iteration = {
            '8': 21,
            '9': 19,
            '10': 17,
            '11': 15,
            '12': 13,
            '13': 11,
            '14': 9,
            '15': 7,
            '16': 5,
            '17': 3,
            '18': 2,
                    
        }
        time_now = datetime.now().time()
        current_hour = time_now.hour
        max_iterations = time_iteration.get(str(current_hour), 0)
        logging.info(f'Установлено количество выгрузок на день: {max_iterations}')
        if max_iterations ==  MAX_ITERATIONS:
            logging.info('Начинаются выгрузки за вчера')
            self.unloading(payment_write_in_txt_a, date_time_yesterday)

            logging.info('Начинаются первые выгрузки за день')
            self.unloading(payment_write_in_txt_w, date_time_today)
            time.sleep(SLEEP)
            self.session_alive()
            time.sleep(SLEEP)

        iteration_count = 0
        while iteration_count != max_iterations:
            logging.info(f"Цикл начало")
            logging.info(f'Выгрузка № {iteration_count}')
            iteration_count += 1
            self.unloading(payment_write_in_txt_a, date_time_today)
            
            self.session_alive()
            time.sleep(SLEEP)
            self.session_alive()
            time.sleep(SLEEP)
        logging.info(f'Выполнены успешно все установленные: {max_iterations}')
        logging.info(f'Программа ждет времени исполнения {time_process}')

    def unloading(self, payment_write, date):
        logging.info('Запущена выгрузка окна(unloading)')
        self.get_account_statements(payment_write, BANK_ACCOUNT_WINDOW, date)
        logging.info('Запущена выгрузка потолки(unloading)')
        self.get_account_statements(payment_write, BANK_ACCOUNT_CEILING, date)
        

if __name__ == "__main__":
    configure_logging()
    logging.info('Программа запущена')
    api_instance = ApiBankOkd()
    api_instance.authorization()
    api_instance.process_data()
    schedule.every().day.at(f"{time_authoriz}").do(api_instance.authorization)
    schedule.every().day.at(f"{time_process}").do(api_instance.process_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
