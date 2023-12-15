import datetime
import time
import schedule


def get_datetime():
    # Первый запуск 8:00
    time_start = datetime.time(8, 00, 00)
    time1 = f'T{time_start}'+"+03:00"
    date = f'{datetime.datetime.now().date()}'
    # здесь лежит дата и время последней выгрузки окон
    DATE_FROM = f"{datetime.datetime.now().date() - datetime.timedelta(days=1)}T19:00:00+03:00"
    print(f"Подготовка...  date_from {DATE_FROM}")
    DATE_TO = date + time1
    print(f"Подготовка...  date_to {DATE_TO}")
    print('Выгрузка! \nПервая выгрузка после ночи сделана, спим 30 минут')

    DATE_FROM = DATE_TO
    time.sleep(10)
    DATE_TO = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z") + "+03:00"

    while DATE_TO != date + 'T19:00:00+03:00':
        print(f"Дата последней выгрузки date_from {DATE_FROM}")
        # ставим дату до текущего момента после 30 минут
        DATE_TO = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z") + "+03:00"
        print(f"Дата выгрузки ДО date_to {DATE_TO}")
        DATE_FROM = DATE_TO
        print('Выгрузка сделана даты изменены, спим 30 минут')
        time.sleep(10)
    

if __name__ == "__main__":
    # Настройка задачи для выполнения в 8:00 утра
    schedule.every().day.at("08:00").do(get_datetime)

    while True:
        schedule.run_pending()
        time.sleep(1)
