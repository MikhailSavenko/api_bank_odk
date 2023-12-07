from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Настройка опций для запуска Chrome в headless режиме
chrome_options = Options()
chrome_options.add_argument("--headless")  # включение headless режима
chrome_options.add_argument("--no-sandbox")  # режим без песочницы
chrome_options.add_argument("--disable-dev-shm-usage")  # отключить использование общей памяти
chrome_options.add_argument("--disable-gpu") 
# Инициализация драйвера Selenium с опциями
driver = webdriver.Chrome(options=chrome_options)

# Открыть страницу входа
driver.get("https://www.e-bgpb.by/sso/!ClientAuth.Login?auth_return_url=https://ulapi.bgpb.by:8243")

# Найти элементы ввода для логина и пароля
login_input = driver.find_element(By.NAME, 'sso_p_Login')
password_input = driver.find_element(By.NAME, 'sso_p_Password')

# Ввести учетные данные
login_input.send_keys('19293924')
password_input.send_keys('ssdvccc22fr')

# Отправить форму
password_input.send_keys(Keys.RETURN)

# Дать время для обработки ответа
time.sleep(5)

# Из них можно будет достать SID
cookies = driver.get_cookies()
print(cookies)  # Выведет список cookies


auth_sid = next((cookie['value'] for cookie in cookies if cookie['name'] == 'auth_sid'), None)
print(auth_sid)
# Закрыть браузер
driver.quit()
