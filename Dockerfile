FROM python:3.11.4

# Установка зависимостей для Chrome
RUN apt-get update && apt-get install -y gnupg2 wget

# Добавление репозитория Google и установка Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get update && apt-get install -y google-chrome-stable

# Установка ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -P ~/ && \
    unzip ~/chromedriver_linux64.zip -d ~/ && \
    rm ~/chromedriver_linux64.zip && \
    mv -f ~/chromedriver /usr/local/bin/chromedriver && \
    chown root:root /usr/local/bin/chromedriver && \
    chmod 0755 /usr/local/bin/chromedriver

# Установка Selenium
RUN pip install selenium

# Копирование вашего скрипта Python в контейнер
COPY get_sid_selenium_headless.py /app/get_sid_selenium_headless.py

# Переход в рабочую директорию
WORKDIR /app

# Запуск скрипта при старте контейнера
CMD ["python", "get_sid_selenium_headless.py"]
