import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

API_KEY = 'YOUR_2CAPTCHA_API_KEY'  # Замените на ваш API-ключ от 2Captcha

def solve_captcha(site_key, page_url):
    captcha_id = requests.post(
        f'https://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}'
    ).json()['request']
    
    # Ожидание решения капчи
    time.sleep(20)
    while True:
        response = requests.get(f'https://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}').json()
        if response['status'] == 1:
            return response['request']
        time.sleep(5)  # Ожидание перед следующим запросом

def load_accounts_and_proxies():
    with open('accs.txt', 'r') as acc_file:
        accounts = [line.strip() for line in acc_file if line.strip()]
    with open('proxys.txt', 'r') as prox_file:
        proxies = [line.strip() for line in prox_file if line.strip()]
    return accounts, proxies

def main():
    accounts, proxies = load_accounts_and_proxies()
    
    for account, proxy in zip(accounts, proxies):
        username, password = account.split(':')
        
        # настройки для использования прокси
        chrome_options = Options()
        chrome_options.add_argument(f'--proxy-server={proxy}')
        
        service = Service(executable_path='chromedriver')  # Убедитесь, что путь к chromedriver верный
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get('https://app.nodepay.ai/login')

        # Вводим данные для входа
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username'))).send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)
        
        # Решение капчи, если она требуется
        try:
            site_key = driver.find_element(By.CLASS_NAME, 'g-recaptcha').get_attribute('data-sitekey')
            captcha_response = solve_captcha(site_key, driver.current_url)
            driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML='{captcha_response}';")
        except Exception as e:
            print(f"No captcha found for {username}.")

        # Посылаем форму
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        # Ждем, пока страница загрузится
        time.sleep(5)

        # Выполнение консольных команд для получения токена
        driver.execute_script("allow_pasting = true;")  # Разрешаем вставку
        np_token = driver.execute_script("return localStorage.getItem('np_token');")
        
        if np_token:
            with open('np_tokens.txt', 'a') as token_file:
                token_file.write(np_token + '\n')
            print(f'Token for {username}: {np_token} saved.')
        else:
            print(f'No np_token found for {username}.')

        driver.quit()

if __name__ == "__main__":
    main()
